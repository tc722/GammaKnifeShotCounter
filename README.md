# Gamma Knife Shot Pattern Counter

This tool streamlines the billing process for Gamma Knife treatments by automating the calculation of required physics complexity codes.

It connects directly to the Gamma Knife Treatment Planning System (TPS) database (PostgreSQL), retrieves the most recent patient plans, and calculates two metrics:
1.  **Total Shot Count** (for CPT Code **77300**)
2.  **Unique Shot Patterns** (for CPT Code **77334**)

## How It Works

### 1. Database Connection
The tool queries the TPS database to fetch the 5 most recent treatment plans, displaying them in a table for selection.

### 2. The Logic: Unique Shot Patterns (CPT 77334)
Rotational symmetry is taken into account when counting the number of unique shot patterns.

**Example of Equivalence:**
The following two shots are considered as the **same physical shot pattern** due to rotational symmetry:

* **Shot A:** `8 | 8 | 8 | 4 | 8 | 8 | 8 | 16`
* **Pattern B:** `4 | 8 | 8 | 8 | 16 | 8 | 8 | 8`

> **Note:** The tool normalizes these patterns before counting. If a plan has 100 shots but they are all variations of the pattern above, the "Unique Pattern Count" will be **1**.

## Configuration

**Important:** This tool requires access to your local Gamma Knife SQL database. You will need add the computer to the allowed-list in your Gamma Knife TPS console.

1. Create a file `config.ini`
2. Copy the following information with your specific TPS database details:

    ```ini
    [Database]
    host = 192.168.x.x      ; The IP address of your GK Database
    port = 5432
    user = guest            ; Verify with your Gamma Knife physicist or Elekta support
    password = your_password; Verify with your Gamma Knife physicist or Elekta support
    name = tpsdb
    ```
