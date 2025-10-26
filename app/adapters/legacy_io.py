"""Legacy I/O adapter for parsing fixed-width data files."""
import csv
import struct
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from decimal import Decimal
import yaml


class FixedWidthParser:
    """Parser for fixed-width legacy data files."""
    
    def __init__(self, spec_file: Path):
        """Initialize parser with a YAML specification file."""
        self.spec = self._load_spec(spec_file)
        self.field_cache = {}
    
    def _load_spec(self, spec_file: Path) -> Dict[str, Any]:
        """Load YAML specification file."""
        with spec_file.open('r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def parse_record(self, record_data: bytes) -> Dict[str, Any]:
        """Parse a single record according to the specification."""
        result = {}
        
        for field_spec in self.spec.get('fields', []):
            field_name = field_spec['name']
            offset = field_spec['offset']
            length = field_spec['length']
            field_type = field_spec.get('type', 'STRING')
            
            # Extract field data
            field_data = record_data[offset:offset + length]
            
            # Parse according to type
            parsed_value = self._parse_field(field_data, field_type, field_spec)
            result[field_name] = parsed_value
        
        return result
    
    def _parse_field(self, field_data: bytes, field_type: str, field_spec: Dict[str, Any]) -> Any:
        """Parse a field according to its type."""
        if field_type == 'STRING':
            # Remove trailing nulls and whitespace
            return field_data.decode('cp437', errors='ignore').rstrip('\x00 \t\n\r')
        
        elif field_type == 'INTEGER':
            if len(field_data) == 2:
                return struct.unpack('<h', field_data)[0]  # 16-bit signed
            elif len(field_data) == 4:
                return struct.unpack('<i', field_data)[0]  # 32-bit signed
            else:
                # Try to parse as string then convert
                try:
                    return int(field_data.decode('cp437', errors='ignore').strip())
                except ValueError:
                    return 0
        
        elif field_type == 'DECIMAL':
            if len(field_data) == 4:
                return Decimal(str(struct.unpack('<f', field_data)[0]))
            elif len(field_data) == 8:
                return Decimal(str(struct.unpack('<d', field_data)[0]))
            else:
                # Try to parse as string then convert
                try:
                    return Decimal(field_data.decode('cp437', errors='ignore').strip())
                except:
                    return Decimal('0')
        
        elif field_type == 'BOOLEAN':
            # Assume 0/1 or True/False
            value = field_data.decode('cp437', errors='ignore').strip()
            return value.lower() in ['1', 'true', 't', 'y', 'yes']
        
        else:
            # Default to string
            return field_data.decode('cp437', errors='ignore').rstrip('\x00 \t\n\r')
    
    def parse_file(self, data_file: Path) -> List[Dict[str, Any]]:
        """Parse an entire data file."""
        records = []
        record_length = self.spec.get('record_length', 128)
        
        with data_file.open('rb') as f:
            while True:
                record_data = f.read(record_length)
                if not record_data:
                    break
                
                if len(record_data) < record_length:
                    # Pad with nulls if record is too short
                    record_data += b'\x00' * (record_length - len(record_data))
                
                try:
                    record = self.parse_record(record_data)
                    records.append(record)
                except Exception as e:
                    print(f"Error parsing record at position {f.tell() - record_length}: {e}")
                    continue
        
        return records


class LegacyDataMapper:
    """Maps legacy data to modern database models."""
    
    def __init__(self, mapping_csv: Path):
        """Initialize mapper with CSV mapping file."""
        self.mappings = self._load_mappings(mapping_csv)
    
    def _load_mappings(self, mapping_csv: Path) -> Dict[str, List[Dict[str, Any]]]:
        """Load field mappings from CSV."""
        mappings = {}
        
        with mapping_csv.open('r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                table = row['new_table']
                if table not in mappings:
                    mappings[table] = []
                mappings[table].append(row)
        
        return mappings
    
    def map_record(self, legacy_record: Dict[str, Any], target_table: str) -> Dict[str, Any]:
        """Map a legacy record to a modern database record."""
        if target_table not in self.mappings:
            return {}
        
        mapped_record = {}
        
        for mapping in self.mappings[target_table]:
            legacy_field = mapping['field']
            new_column = mapping['new_column']
            field_type = mapping['type']
            
            if legacy_field in legacy_record:
                value = legacy_record[legacy_field]
                mapped_record[new_column] = self._convert_value(value, field_type)
        
        return mapped_record
    
    def _convert_value(self, value: Any, field_type: str) -> Any:
        """Convert a value to the appropriate type."""
        if value is None:
            return None
        
        if field_type == 'INTEGER':
            try:
                return int(value)
            except (ValueError, TypeError):
                return 0
        
        elif field_type == 'DECIMAL':
            try:
                return Decimal(str(value))
            except:
                return Decimal('0')
        
        elif field_type == 'BOOLEAN':
            if isinstance(value, bool):
                return value
            return str(value).lower() in ['1', 'true', 't', 'y', 'yes']
        
        else:
            return str(value)


# Sample data generators for testing
def create_sample_products_data() -> List[Dict[str, Any]]:
    """Create sample product data for testing."""
    return [
        {
            'sku': 'PAINT-001',
            'name': 'Trade Paint Base',
            'description': 'White base paint for tinting',
            'density_kg_per_l': Decimal('1.2'),
            'abv_percent': None,
            'is_active': True
        },
        {
            'sku': 'PAINT-002', 
            'name': 'Clear Varnish',
            'description': 'Clear protective varnish',
            'density_kg_per_l': Decimal('0.9'),
            'abv_percent': None,
            'is_active': True
        },
        {
            'sku': 'SOLVENT-001',
            'name': 'Paint Thinner',
            'description': 'Mineral spirits for thinning paint',
            'density_kg_per_l': Decimal('0.8'),
            'abv_percent': None,
            'is_active': True
        }
    ]


def create_sample_customers_data() -> List[Dict[str, Any]]:
    """Create sample customer data for testing."""
    return [
        {
            'code': 'CUST-001',
            'name': 'Paint Factory Bayswater',
            'contact_person': 'John Smith',
            'email': 'john@paintfactory.com.au',
            'phone': '+61 3 9876 5432',
            'address': 'Unit 31,172 Canterbury Road\nBAYSWATER NORTH 3153\nAU',
            'tax_rate': Decimal('10.0'),
            'is_active': True
        },
        {
            'code': 'CUST-002',
            'name': 'Trade Paint Supplies',
            'contact_person': 'Jane Doe',
            'email': 'jane@tradepaint.com.au',
            'phone': '+61 3 1234 5678',
            'address': '123 Industrial Way\nMELBOURNE 3000\nAU',
            'tax_rate': Decimal('10.0'),
            'is_active': True
        }
    ]


def create_sample_pack_units_data() -> List[Dict[str, Any]]:
    """Create sample pack unit data for testing."""
    return [
        {
            'code': 'CAN',
            'name': 'Can',
            'description': 'Standard paint can',
            'is_active': True
        },
        {
            'code': '4PK',
            'name': '4-Pack',
            'description': 'Pack of 4 cans',
            'is_active': True
        },
        {
            'code': 'CTN',
            'name': 'Carton',
            'description': 'Carton of 12 cans',
            'is_active': True
        }
    ]


def create_sample_batch_data() -> List[Dict[str, Any]]:
    """Create sample batch data for testing."""
    return [
        {
            'batch_code': 'B060149',
            'work_order_id': 'WO-001',
            'product_id': 'PAINT-001',
            'planned_quantity_kg': Decimal('370.0'),
            'actual_quantity_kg': Decimal('365.5'),
            'status': 'completed',
            'started_at': '2024-01-15T08:00:00',
            'completed_at': '2024-01-15T16:30:00'
        }
    ]


def create_sample_invoice_data() -> List[Dict[str, Any]]:
    """Create sample invoice data for testing."""
    return [
        {
            'invoice_number': '00086633',
            'customer_id': 'CUST-001',
            'sales_order_id': 'SO-001',
            'invoice_date': '2024-01-20',
            'due_date': '2024-02-19',
            'status': 'issued',
            'subtotal_ex_tax': Decimal('456.22'),
            'tax_amount': Decimal('45.62'),
            'total_inc_tax': Decimal('501.84')
        }
    ]