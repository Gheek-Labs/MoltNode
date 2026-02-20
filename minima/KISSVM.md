# KISSVM Scripting Language Reference

Complete glossary of the KISSVM (Keep It Simple Stupid Virtual Machine) language used in Minima transaction scripts.

**Related:** [COMMANDS.md](COMMANDS.md) | [ONCHAIN_RECORDS.md](ONCHAIN_RECORDS.md) | [RESPONSE_SCHEMAS.md](RESPONSE_SCHEMAS.md)

---

## Overview

Every coin on Minima has a script that determines who can spend it. The script must return `TRUE` for the transaction to be valid. The simplest script is:

```
RETURN SIGNEDBY(0x<publickey>)
```

This returns `TRUE` only if the transaction is signed by the given key.

---

## Types

| Type | Format | Examples |
|------|--------|---------|
| NUMBER | Decimal, optionally negative | `42`, `3.14`, `-1`, `0.000000001` |
| HEX | `0x` prefix + hex chars | `0xABCD`, `0x00` |
| STRING | `[` and `]` delimiters | `[hello world]`, `[data]` |
| BOOLEAN | `TRUE` or `FALSE` | `TRUE`, `FALSE` |

> **AGENT WARNING:** Strings use square brackets `[` `]`, NOT quotes. `"hello"` is invalid — use `[hello]` instead.

### Type Conversions

| Function | Description |
|----------|-------------|
| `BOOL(value)` | Convert to TRUE or FALSE |
| `HEX(script)` | Convert SCRIPT to HEX |
| `NUMBER(hex)` | Convert HEX to NUMBER |
| `STRING(hex)` | Convert HEX value to SCRIPT |
| `UTF8(hex)` | Convert HEX to UTF8 string |
| `ASCII(hex)` | Convert HEX to ASCII string |

---

## Globals

Globals are read-only values available in every script, describing the current coin and transaction context.

| Global | Type | Description |
|--------|------|-------------|
| `@BLOCK` | NUMBER | Current block number |
| `@BLOCKMILLI` | NUMBER | Current block time in milliseconds since epoch (Jan 1 1970) |
| `@CREATED` | NUMBER | Block number when this coin was created |
| `@COINAGE` | NUMBER | `@BLOCK - @CREATED` — age of the coin in blocks |
| `@INPUT` | NUMBER | Input index of this coin in the transaction (first = 0) |
| `@COINID` | HEX | The coin's unique identifier |
| `@AMOUNT` | NUMBER | The coin's amount |
| `@ADDRESS` | HEX | The coin's address |
| `@TOKENID` | HEX | The coin's token ID (`0x00` = native Minima) |
| `@SCRIPT` | STRING | The script text of this coin |
| `@TOTIN` | NUMBER | Total number of input coins in the transaction |
| `@TOTOUT` | NUMBER | Total number of output coins in the transaction |

---

## Operators

### Arithmetic

| Operator | Description |
|----------|-------------|
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |
| `%` | Modulo |
| `<<` | Left shift |
| `>>` | Right shift |
| `&` | Bitwise AND |
| `\|` | Bitwise OR |
| `^` | Bitwise XOR |
| `NEG` | Negate (unary) |

### Comparison

| Operator | Description |
|----------|-------------|
| `EQ` | Equal |
| `NEQ` | Not equal |
| `GT` | Greater than |
| `GTE` | Greater than or equal |
| `LT` | Less than |
| `LTE` | Less than or equal |

### Logical

| Operator | Description |
|----------|-------------|
| `AND` | Logical AND |
| `OR` | Logical OR |
| `XOR` | Logical XOR |
| `NAND` | Logical NAND |
| `NOR` | Logical NOR |
| `NXOR` | Logical NXOR |
| `NOT` | Logical NOT (unary) |

---

## Statements

| Statement | Syntax | Description |
|-----------|--------|-------------|
| `LET` | `LET x = expr` | Assign a value to a variable |
| `LET` (array) | `LET (a b c) = expr` | Assign to an array, access with `GET` |
| `IF` | `IF expr THEN ... ELSEIF expr THEN ... ELSE ... ENDIF` | Conditional branching |
| `WHILE` | `WHILE expr DO ... ENDWHILE` | Loop |
| `RETURN` | `RETURN expr` | Return a value (TRUE = script passes, FALSE = fails) |
| `ASSERT` | `ASSERT expr` | Fail immediately if expr is FALSE |
| `EXEC` | `EXEC expr` | Execute a script string dynamically |
| `MAST` | `MAST expr` | Execute a Merkle Abstract Syntax Tree script |

> Variables must be lowercase letters only: `a`, `myvar`, `total` — no numbers, no uppercase.

---

## Functions — Data Manipulation

| Function | Signature | Description |
|----------|-----------|-------------|
| `CONCAT` | `CONCAT(hex1 hex2 ... hexN)` | Concatenate HEX values |
| `LEN` | `LEN(hex\|script)` | Length of data |
| `REV` | `REV(hex)` | Reverse the data |
| `SUBSET` | `SUBSET(hex start length)` | Extract a substring of HEX data |
| `SETLEN` | `SETLEN(number hex)` | Set the byte length — trims or zero-pads |
| `OVERWRITE` | `OVERWRITE(hex1 pos1 hex2 pos2 length)` | Copy bytes from hex2 into hex1 |
| `REPLACE` | `REPLACE(string find replace)` | Replace all occurrences of `find` with `replace` in string |
| `SUBSTR` | `SUBSTR(start length string)` | Get substring |

## Functions — Arrays

| Function | Signature | Description |
|----------|-----------|-------------|
| `GET` | `GET(n1 n2 ... nN)` | Get value from array set with `LET (...)` |
| `EXISTS` | `EXISTS(n1 n2 ... nN)` | Check if array value exists |

## Functions — Math

| Function | Signature | Description |
|----------|-----------|-------------|
| `ABS` | `ABS(number)` | Absolute value |
| `CEIL` | `CEIL(number)` | Round up |
| `FLOOR` | `FLOOR(number)` | Round down |
| `MIN` | `MIN(a b)` | Minimum of two numbers |
| `MAX` | `MAX(a b)` | Maximum of two numbers |
| `INC` | `INC(number)` | Increment (+1) |
| `DEC` | `DEC(number)` | Decrement (-1) |
| `POW` | `POW(base exp)` | Power (exp must be whole number) |
| `SQRT` | `SQRT(number)` | Square root |
| `SIGDIG` | `SIGDIG(number digits)` | Set significant digits |

## Functions — Bit Operations

| Function | Signature | Description |
|----------|-----------|-------------|
| `BITSET` | `BITSET(hex position boolean)` | Set bit at position to 0 or 1 |
| `BITGET` | `BITGET(hex position)` | Get boolean value of bit at position |
| `BITCOUNT` | `BITCOUNT(hex)` | Count number of bits set |

## Functions — Cryptography

| Function | Signature | Description |
|----------|-----------|-------------|
| `SHA2` | `SHA2(hex\|string)` | SHA-256 hash |
| `SHA3` | `SHA3(hex\|string)` | SHA3/Keccak-256 hash (Minima default) |
| `SIGNEDBY` | `SIGNEDBY(publickey)` | TRUE if transaction is signed by this key |
| `MULTISIG` | `MULTISIG(n key1 key2 ... keyN)` | TRUE if signed by N of the listed keys |
| `CHECKSIG` | `CHECKSIG(publickey data signature)` | Verify a signature against data |
| `PROOF` | `PROOF(data root proof)` | Verify MMR proof. Use 0 for non-sum trees |

## Functions — Transaction Introspection

| Function | Signature | Description |
|----------|-----------|-------------|
| `GETOUTADDR` | `GETOUTADDR(index)` | HEX address of output at index |
| `GETOUTAMT` | `GETOUTAMT(index)` | Amount of output at index |
| `GETOUTTOK` | `GETOUTTOK(index)` | Token ID of output at index |
| `GETOUTKEEPSTATE` | `GETOUTKEEPSTATE(index)` | Whether output keeps state |
| `VERIFYOUT` | `VERIFYOUT(index address amount tokenid keepstate)` | Verify output has expected values |
| `GETINADDR` | `GETINADDR(index)` | HEX address of input at index |
| `GETINAMT` | `GETINAMT(index)` | Amount of input at index |
| `GETINTOK` | `GETINTOK(index)` | Token ID of input at index |
| `VERIFYIN` | `VERIFYIN(index address amount tokenid)` | Verify input has expected values |
| `SUMINPUTS` | `SUMINPUTS(tokenid)` | Sum of all input amounts for a token |
| `SUMOUTPUTS` | `SUMOUTPUTS(tokenid)` | Sum of all output amounts for a token |

## Functions — State Variables

| Function | Signature | Description |
|----------|-----------|-------------|
| `STATE` | `STATE(port)` | Get state variable value at port (0–255) for current transaction |
| `PREVSTATE` | `PREVSTATE(port)` | Get state value stored when the coin was created (MMR data) |
| `SAMESTATE` | `SAMESTATE(start end)` | TRUE if previous and current state match for ports start..end |

> **State variables** are the mechanism for embedding arbitrary data in transactions.
> Use `txnstate id:<id> port:<n> value:<hex>` to set them when building transactions.

## Functions — Script Execution

| Function | Signature | Description |
|----------|-----------|-------------|
| `ADDRESS` | `ADDRESS(script)` | Compute the address of a script |
| `FUNCTION` | `FUNCTION(script val1 val2 ... valN)` | Run script with `$1`, `$2`.. replaced by values; returns `returnvalue` |

---

## Common Script Patterns

### Simple ownership (default)
```
RETURN SIGNEDBY(0x<yourpublickey>)
```

### Multi-signature (2 of 3)
```
RETURN MULTISIG(2 0x<key1> 0x<key2> 0x<key3>)
```

### Time-locked coin (spendable after block 2000000)
```
IF @BLOCK GTE 2000000 THEN
    RETURN SIGNEDBY(0x<recipientkey>)
ENDIF
RETURN FALSE
```

### Coin age check (must be at least 100 blocks old)
```
ASSERT @COINAGE GTE 100
RETURN SIGNEDBY(0x<yourkey>)
```

### Hash-locked coin (anyone with the preimage can spend)
```
IF SHA3(STATE(0)) EQ 0x<targethash> THEN
    RETURN TRUE
ENDIF
RETURN FALSE
```

### Verifiable output (enforce where funds go)
```
ASSERT VERIFYOUT(0 0x<recipientaddr> @AMOUNT @TOKENID TRUE)
RETURN SIGNEDBY(0x<senderkey>)
```

### Stateful contract (value tracking via PREVSTATE)
```
LET oldval = PREVSTATE(0)
LET newval = STATE(0)
ASSERT newval GT oldval
RETURN SIGNEDBY(0x<controllerkey>)
```

### Token burn (total out < total in)
```
LET burnamt = SUMINPUTS(0x00) - SUMOUTPUTS(0x00)
ASSERT burnamt GT 0
RETURN SIGNEDBY(0x<burnerkey>)
```

### Data record script (always spendable by owner)
```
RETURN SIGNEDBY(0x<yourkey>)
```
> For on-chain data records, the script is typically just `RETURN SIGNEDBY(...)`.
> The data goes into **state variables**, not the script itself.
> See [ONCHAIN_RECORDS.md](ONCHAIN_RECORDS.md) for the full recipe.

---

## Grammar (Formal)

```
ADDRESS   → ADDRESS ( BLOCK )
BLOCK     → STATEMENT_1 STATEMENT_2 ... STATEMENT_n
STATEMENT → LET VARIABLE = EXPRESSION
          | LET ( EXPRESSION_1 ... EXPRESSION_n ) = EXPRESSION
          | IF EXPRESSION THEN BLOCK [ELSEIF EXPRESSION THEN BLOCK] [ELSE BLOCK] ENDIF
          | WHILE EXPRESSION DO BLOCK ENDWHILE
          | EXEC EXPRESSION
          | MAST EXPRESSION
          | ASSERT EXPRESSION
          | RETURN EXPRESSION
EXPRESSION → RELATION
RELATION   → LOGIC (AND|OR|XOR|NAND|NOR|NXOR) LOGIC | LOGIC
LOGIC      → OPERATION (EQ|NEQ|GT|GTE|LT|LTE) OPERATION | OPERATION
OPERATION  → ADDSUB (&|||^) ADDSUB | ADDSUB
ADDSUB     → MULDIV (+|-|%|<<|>>) MULDIV | MULDIV
MULDIV     → PRIME (*|/) PRIME | PRIME
PRIME      → NOT PRIME | NEG PRIME | PRIME | BASEUNIT
BASEUNIT   → VARIABLE | VALUE | GLOBAL | FUNCTION | ( EXPRESSION )
VARIABLE   → [a-z]+
VALUE      → NUMBER | HEX | STRING | BOOLEAN
```
