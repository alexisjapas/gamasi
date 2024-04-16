# Deep recursive copy TODO

# Universe recursive equality TODO

# Agents path stability TODO

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

# TODO Find why some agents pop from nowhere
a = simulation["universe"].population[
    data["agents_statistics"]["travelled_distance"].idxmin()
]
print(a.birth_date)
print(a.position)
print(a.framescount)

from src.Brain import Abilities

for a in simulation["universe"].population.values():
    if a.position.y == 40 and a.position.x == 111:
        print(a)

a = simulation["universe"].population[1140]
print(a.framescount)
print(a.parents)
print(a.birth_date)
print()

b = simulation["universe"].population[864]
print(b.framescount)
print(b.parents)
print(len(b.children))
for c in b.children:
    print(c.id, c.birth_date)
for ac in b.actions:
    print(ac)
