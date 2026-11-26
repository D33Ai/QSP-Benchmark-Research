# Hidden Parity in Sparse Integer Partition

**Kellar A. Moore and Troy Hamner · D33 AI · Review preprint v1.0 · November 25, 2026**

[Read the paper (PDF)](Hidden_Parity_in_Sparse_Integer_Partition.pdf) · [Editable review manuscript (Word)](Hidden_Parity_in_Sparse_Integer_Partition.docx) · [Manuscript source](manuscript.md) · [Complete replay archive](QSP_Hidden_Parity_Review_Materials.zip)

The minimum flat cover of the Fano construction by conflicts justified by one original line is exactly $7\cdot 2^{3g-2}$ for odd block width $g$. For the 658-weight instance this is 234,881,024 entries. A solver reads the same integers, reconstructs seven parity variables, and certifies infeasibility by counting pairs.

## Technical review

- Check whether the partial assignments and allowed inference in Section 3 are sufficiently specified. Try to cover two of the private extensions with a single valid conflict.
- Inspect the path recognition and reconstruction code. Look for a layout the recognizer accepts for which the parity image gives the wrong partition decision.
- Replay the numeric examples and small exhaustive tests. If reporting a discrepancy, include the input integers, command, expected and observed result, Python version and solver version.

The full review replay on November 25 used Python 3.12.14 and Z3 4.13.3. The 12 SAT decisions and archived structured-solver and counting records matched. The width-three cover check enumerated 2,097,152 assignments and verified 896 private witnesses. See Appendix B in the manuscript for commands. The archive contains its own SHA-256 manifest.

The paper is a public preprint for review. It gives a result for a restricted certificate format. P versus NP remains open.
