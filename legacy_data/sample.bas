REM Sample QuickBASIC source file for testing legacy audit
TYPE PRODUCT
    sku AS STRING*20
    name AS STRING*50
    description AS STRING*100
    density AS SINGLE
    abv AS SINGLE
    active AS INTEGER
END TYPE

TYPE CUSTOMER
    code AS STRING*10
    name AS STRING*50
    address1 AS STRING*50
    address2 AS STRING*50
    city AS STRING*30
    postal AS STRING*10
    country AS STRING*2
    contact AS STRING*50
    email AS STRING*50
    phone AS STRING*20
    active AS INTEGER
END TYPE

TYPE INVENTORY
    lot_code AS STRING*20
    product_sku AS STRING*20
    quantity AS SINGLE
    unit_cost AS SINGLE
    supplier_code AS STRING*10
    received_date AS STRING*10
    expiry_date AS STRING*10
    active AS INTEGER
END TYPE

REM Main program
OPEN "products.dat" FOR RANDOM AS #1 LEN = LEN(PRODUCT)
OPEN "customers.dat" FOR RANDOM AS #2 LEN = LEN(CUSTOMER)
OPEN "inventory.dat" FOR RANDOM AS #3 LEN = LEN(INVENTORY)

FIELD #1, 20 AS sku$, 50 AS name$, 100 AS description$, 4 AS density$, 4 AS abv$, 2 AS active$
FIELD #2, 10 AS code$, 50 AS name$, 50 AS addr1$, 50 AS addr2$, 30 AS city$, 10 AS postal$, 2 AS country$, 50 AS contact$, 50 AS email$, 20 AS phone$, 2 AS active$
FIELD #3, 20 AS lot_code$, 20 AS product_sku$, 4 AS quantity$, 4 AS unit_cost$, 10 AS supplier_code$, 10 AS received_date$, 10 AS expiry_date$, 2 AS active$

REM Sample data operations
DIM prod AS PRODUCT
prod.sku = "PAINT-001"
prod.name = "Trade Paint Base"
prod.description = "White base paint for tinting"
prod.density = 1.2
prod.abv = 0
prod.active = 1

PUT #1, 1, prod

CLOSE
