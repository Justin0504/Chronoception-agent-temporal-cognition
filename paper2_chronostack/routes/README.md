# ChronoStack — installation routes

Paper 2's thesis: chronoception cannot be acquired from token-only training
(Paper 1, CIT), so it must be **installed**. ChronoStack enumerates the routes
to install it and measures the ε reduction each one buys on ChronoBench.

| Route | Idea | First proof point | Status |
|---|---|---|---|
| 1 Loss extension | wall-clock-supported SFT / RL reward | A.1 toy positive control (`../toy_a1/`) | partial (1.5B crosses ε\*, 7B does not) |
| **2 Tool interface** | learned policy over `get_current_time()` | **availability-vs-use MVP** ([`02_tool_interface.md`](02_tool_interface.md)) | **MVP scaffolded** |
| 3 Scaffolding | harness exposes a live τ_step counter, deadline, budget remaining | budget-honoring loop (on branch `zijian/paper2-scaffolding`) | MVP + budget sweep done |
| 4 Architectural primitive | a new input modality that takes wall-clock as an argument | — | not started |

Each route is judged the same way: does it move a ChronoBench axis (ε, CAR, or
|ρ|) toward grounded, where Paper 1 showed token-only training and static
injection cannot?
