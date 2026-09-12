# Evidence import boundary

`pytest-junit.xml` is a minimal, path-free JUnit inventory from the pinned
temporary clone (90 passed). `coverage.xml` contains only an aggregate inventory
record. The JUnit identities are promoted only by `../mapping.yaml`; coverage.py
remains inventory and can never satisfy an obligation by itself.
