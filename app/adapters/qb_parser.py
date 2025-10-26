#!/usr/bin/env python3
"""
QuickBASIC random-access file parser.
Parses QB MSF (MS FILES) binary format files.
"""

import struct
from pathlib import Path
from typing import List, Dict, Optional
from decimal import Decimal


class QBFileParser:
    """Parse QuickBASIC random-access files (.MSF extension)."""
    
    # Record layouts from QB TYPE definitions
    # Based on MSRMAT.INC: RcdFmtmsrmat structure
    # QuickBASIC stores records as fixed-width binary
    # INTEGER = 2 bytes, SINGLE = 4 bytes, STRING * n = n bytes, CURRENCY = 8 bytes
    RAW_MATERIAL_LAYOUT = [
        ('no', 'i'),            # INTEGER
        ('Desc1', '25s'),       # STRING * 25
        ('Desc2', '25s'),       # STRING * 25
        ('purqty', 'i'),        # INTEGER
        ('Search', '5s'),       # STRING * 5
        ('Sg', 'f'),           # SINGLE (float)
        ('PurCost', 'f'),       # SINGLE
        ('PurUnit', '2s'),      # STRING * 2
        ('UseCost', 'f'),       # SINGLE
        ('UseUnit', '2s'),      # STRING * 2
        ('Dealcost', 'f'),      # SINGLE
        ('SupUnit', '2s'),      # STRING * 2
        ('Group', 'i'),         # INTEGER
        ('Active', '1s'),       # STRING * 1
        ('Volsolid', 'f'),      # SINGLE
        ('Solidsg', 'f'),      # SINGLE
        ('Wtsolid', 'f'),      # SINGLE
        ('Notes', '25s'),      # STRING * 25
        ('soh', 'f'),          # SINGLE
        ('Osoh', 'f'),         # SINGLE
        ('Date', '8s'),        # STRING * 8
        ('hazard', '1s'),      # STRING * 1
        ('cond', '1s'),        # STRING * 1
        ('altno1', 'i'),       # altno(1)
        ('altno2', 'i'),       # altno(2)
        ('altno3', 'i'),       # altno(3)
        ('altno4', 'i'),       # altno(4)
        ('altno5', 'i'),       # altno(5)
        ('msdsflag', '1s'),    # STRING * 1
        ('searchs', '8s'),     # STRING * 8
        ('soo', 'i'),          # INTEGER
        ('sip', 'f'),          # SINGLE
        ('sohv', 'f'),         # SINGLE
        ('restock', 'f'),      # SINGLE
        ('used', 'f'),         # SINGLE
        ('ean13', 'q'),        # CURRENCY (8 bytes, scaled integer)
        ('lastpur', '8s'),     # STRING * 8
        ('supqty', 'f'),       # SINGLE
        ('filler', '60s'),     # STRING * 60
    ]
    
    # Batch record layout from MSBATCH.INC: ~512 bytes
    BATCH_LAYOUT = {
        'bno': ('i', 2),  # batch_no
        'year': ('2s', 2),  # STRING * 2
        'form': ('4s', 4),  # STRING * 4
        'revision': ('i', 2),
        'SorW': ('1s', 1),  # S/W type
        'class': ('i', 2),
        'yld': ('f', 4),  # yield
        'ayld': ('f', 4),  # actual yield
        # ... many more fields ...
    }
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        
    def parse_raw_materials(self) -> List[Dict]:
        """
        Parse MSRMNEW.MSF raw material file.
        Returns list of raw material dictionaries.
        """
        records = []
        
        # Calculate record size
        rec_size = 0
        for field_name, field_type in self.RAW_MATERIAL_LAYOUT:
            if field_type == 'i':
                rec_size += 2  # INTEGER
            elif field_type == 'f':
                rec_size += 4  # SINGLE
            elif field_type == 'q':
                rec_size += 8  # CURRENCY
            elif field_type.endswith('s'):
                rec_size += int(field_type.replace('s', ''))
        
        # Read file in binary mode
        with open(self.filepath, 'rb') as f:
            while True:
                # Read one record
                rec_bytes = f.read(rec_size)
                if len(rec_bytes) < rec_size:
                    break
                
                # Parse record based on structure
                parsed = self._parse_raw_material_record(rec_bytes)
                if parsed and parsed.get('no', 0) > 0:  # Valid record
                    records.append(parsed)
        
        return records
    
    def _parse_raw_material_record(self, data: bytes) -> Optional[Dict]:
        """Parse a single raw material record."""
        offset = 0
        record = {}
        
        for field_name, field_type in self.RAW_MATERIAL_LAYOUT:
            if field_type == 'i':  # INTEGER (2 bytes)
                value = struct.unpack('<h', data[offset:offset+2])[0]  # Little-endian
                record[field_name] = value
                offset += 2
            elif field_type == 'f':  # SINGLE (4 bytes)
                value = struct.unpack('<f', data[offset:offset+4])[0]  # Little-endian float
                record[field_name] = value
                offset += 4
            elif field_type == 'q':  # CURRENCY (8 bytes)
                # QB CURRENCY is 64-bit scaled integer
                value = struct.unpack('<q', data[offset:offset+8])[0] / 10000.0
                record[field_name] = value
                offset += 8
            elif field_type.endswith('s'):  # STRING
                str_len = int(field_type.replace('s', ''))
                value_bytes = data[offset:offset+str_len]
                try:
                    value = value_bytes.rstrip(b'\x00').decode('cp437', errors='ignore').strip()
                except:
                    value = ''
                record[field_name] = value
                offset += str_len
        
        return record
    
    def parse_batch_records(self) -> List[Dict]:
        """
        Parse MSBATCH.MSF batch file.
        Returns list of batch dictionaries.
        """
        records = []
        rec_size = 512  # MSBATCH record size
        
        with open(self.filepath, 'rb') as f:
            while True:
                rec_bytes = f.read(rec_size)
                if len(rec_bytes) < rec_size:
                    break
                
                # Parse basic fields
                batch_no = struct.unpack('>h', rec_bytes[0:2])[0]
                year = rec_bytes[2:4].decode('cp437', errors='ignore')
                formula = rec_bytes[4:8].decode('cp437', errors='ignore')
                revision = struct.unpack('>h', rec_bytes[8:10])[0]
                
                if batch_no > 0:  # Valid record
                    records.append({
                        'batch_no': batch_no,
                        'year': year,
                        'formula': formula,
                        'revision': revision,
                        # TODO: Parse remaining 500+ bytes
                    })
        
        return records
    
    def parse_line_file(self, rec_size: int = 160) -> List[Dict]:
        """
        Generic line file parser (for formulas, orders, etc.).
        """
        records = []
        
        with open(self.filepath, 'rb') as f:
            while True:
                rec_bytes = f.read(rec_size)
                if len(rec_bytes) < rec_size:
                    break
                
                # Try to parse as text first (QB files may have ASCII sections)
                try:
                    text = rec_bytes.decode('cp437', errors='ignore').strip()
                    if text:
                        records.append({'content': text})
                except:
                    pass
        
        return records


def parse_qb_file(filepath: Path, file_type: str = 'auto') -> List[Dict]:
    """
    Convenience function to parse a QB file.
    
    Args:
        filepath: Path to QB file
        file_type: Type of file ('raw_materials', 'batches', 'auto')
    
    Returns:
        List of parsed records as dictionaries
    """
    parser = QBFileParser(filepath)
    
    if file_type == 'raw_materials' or (file_type == 'auto' and 'rmat' in filepath.name.lower()):
        return parser.parse_raw_materials()
    elif file_type == 'batches' or (file_type == 'auto' and 'batch' in filepath.name.lower()):
        return parser.parse_batch_records()
    else:
        return parser.parse_line_file()

