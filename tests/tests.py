# Deep recursive copy TODO

# Universe recursive equality TODO

# Stability tests TODO
## Gathering data
errors_births_after_end = []
errors_birth_dates = []

for k, a in simulation["universe"].population.items():
    # Births after end
    if a.birth_date > simulation["timings"]["stop"]:
        errors_births_after_end.append(a)

    # Children younger than agent
    if a.children:
        for c in a.children:
            if a.birth_date > c.birth_date:
                errors_birth_dates.append((a, c))
print(simulation["timings"]["stop"])
## Checking tests
### Births after the end of the simulation
print(errors_births_after_end)
print(len(errors_births_after_end))
### Children are younger than their parents
print(errors_birth_dates)
