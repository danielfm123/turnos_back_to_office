import pulp
import itertools
import pandas as pd

pref = pd.read_excel("data_con_pref.xlsx","pref")
pref = pref.fillna(0)
pref = pref.set_index('colab')
print(pref)
#escalado a 1 y doble ponderación de negativos
for c in pref.index:
    pref.loc[c,:] = pref.loc[c,:]/pref.loc[c,:].abs().sum()
    pref.loc[c,:] = [x if x > 0 else 2*x for x in pref.loc[c,:]]
print(pref)

team = pd.read_excel("data_con_pref.xlsx","team")
team = team.set_index('colab')
print(team)


# indices
dias = pref.columns
emp = pref.index
teams = set(team["team"])

#definir problema
prob = pulp.LpProblem("DIAS", pulp.LpMaximize)

# variables
CD = {e:{d:pulp.LpVariable(cat ='Binary', name ='{} el {}'.format(e, d)) for d in dias} for e in emp}
TD = {t:{d:pulp.LpVariable(cat ='Binary', name ='{} el {}'.format(t, d)) for d in dias} for t in teams}

#Obj
prob += pulp.lpSum([ CD[e][d] * pref.loc[e, d] - (1 - CD[e][d]) * pref.loc[e, d] for e, d in itertools.product(emp, dias)])

# todos van al menos 2 veces a la semana
for e in emp:
    prob += pulp.lpSum([CD[e][d] for d in dias]) >= 1

# cada team tiene su dia
for t in teams:
    prob += pulp.lpSum([TD[t][d] for d in dias]) == 1

# no puede haber mas de 10 personas cada dia
for d in dias:
    prob += pulp.lpSum([CD[e][d] for e in emp]) <= 10

#los van en el dia del team
for e, t, d in itertools.product(emp,teams,dias):
    if team[e] == t:
#        print("{} del {} el {}".format(e,t,d))
        prob += CD[e][d] >= TD[t][d]
#        pass

solver = pulp.getSolver('PULP_CBC_CMD')
prob.solve(solver)

print("empleados")
for e,d in itertools.product(emp,dias):
    if(pulp.value(CD[e][d]) > 0.9):
        print('{} va el {} y esta {}'.format(e,d,'ok' if pref.loc[e,d] > 0 else 'mal'))

print("teams")
for t,d in itertools.product(teams,dias):
    if(pulp.value(TD[t][d]) > 0.9):
        print('{} va el {}'.format(t,d))

print("Valor Objetivo")
print(pulp.value(prob.objective))
