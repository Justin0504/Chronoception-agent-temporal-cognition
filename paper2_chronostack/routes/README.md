# ChronoStack — installation routes

Paper 2's thesis: chronoception cannot be acquired from token-only training
(Paper 1, CIT), so it must be **installed**. ChronoStack enumerates the routes
to install it and measures the ε reduction each one buys on ChronoBench.

| Route | Idea | First proof point | Status |
|---|---|---|---|
| 1 Loss extension | wall-clock-supported SFT / RL reward | A.1 toy positive control (`../toy_a1/`) | partial (1.5B crosses ε\*, 7B does not) |
| 2 Tool interface | learned policy over `get_current_time()` | availability-vs-use MVP ([`02_tool_interface.md`](02_tool_interface.md)) | MVP run: grounds non-reasoning; fails reasoning (Hidden-Time) |
| 3 Scaffolding | harness exposes a live τ_step counter, deadline, budget remaining | budget-honoring loop ([`03_scaffolding.md`](03_scaffolding.md)) | MVP + budget sweep: eliminates deadline overruns |
| **4 Architectural primitive** | wall-clock as a first-class learned input | time-channel interface ([`04_architectural_primitive.md`](04_architectural_primitive.md)) | **interface implemented; training experiment pre-registered (GPU)** |

Each route is judged the same way: does it move a ChronoBench axis (ε, CAR, or
|ρ|) toward grounded, where Paper 1 showed token-only training and static
injection cannot?

Note on branches: routes 2/3/4 were developed on separate feature branches
(`zijian/paper2-{tool-interface,scaffolding,architectural}`); each branch's
README reflects that branch's route. Merge resolves to this combined table.
