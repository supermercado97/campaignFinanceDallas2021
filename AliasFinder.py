"""

notes:
the walne family at 10020 caribou also has an address at 120 reflex dr
PO Box 71202 has many seemingly unrelated people using this address
PO Box 267 couple seemingly unrelated people
"""
from prettytable import PrettyTable
from statistics import mean, multimode, quantiles
import pandas as pd
import sys, numpy, spacy, json

# INPUT VARIABLES and OUTPUT FILES
aliasFile = 'DonorAliases_test.json'
householdFile = 'SharedAddresses.json'
contributorsDoc = "Campaign_Finance (2).xlsx"
SEMANTIC_SIM_THRESHOLD = 0.73

numpy.set_printoptions(threshold=sys.maxsize)
nlp = spacy.load("en_core_web_lg")
pd.options.display.max_columns = None

financeDF = pd.read_excel(contributorsDoc)
contributorDF = financeDF.loc[(financeDF['Contact Type'] == "Contributor")]
uniqueAddresses = set(financeDF["Street "].unique().tolist())

def semanticNameCheck(name1, name2, threshold):
    name1_doc = nlp(name1)
    name2_doc = nlp(name2)
    sim = name1_doc.similarity(name2_doc)
    if sim > threshold:
        return True
    return False

# let's make sure the 'name' isn't already an alias
def isKnownAlias(name, aliases):
    for knownAliases in aliases.values():
        if (name in knownAliases):
            return True
    return False

aliases = {}
household = {}
for address in uniqueAddresses:
    addyDF = financeDF[financeDF["Street "] == address]

    # 3. all contributions at an address to any council member/mayor
    uniqueCandidatesAtAddress = set(addyDF["Candidate Name"].unique().tolist())
    contributionsToCandidatesAtAddress = dict.fromkeys(uniqueCandidatesAtAddress, 0)
    for candidate in uniqueCandidatesAtAddress:
        contributionsToCandidatesAtAddress[candidate] += round(sum(addyDF[addyDF["Candidate Name"] == candidate].Amount.values.tolist()),2)
        #suspiciousDoc.write(address + " donated $" + contributionsToCandidatesAtAddress[candidate] + " to " + candidate)

    # 2. all contributions at an address where the first and last names match
    uniqueNamesAtAddress = set(addyDF['Upper Combined Names'].unique().tolist())
    for name in uniqueNamesAtAddress:
        if (name == " " or isKnownAlias(name, aliases) or "AND" in name or "&" in name):
            continue
        if ("III" in name or "II" in name or "1" in name or "2" in name):
            lastName = name.split(" ")[-2]
        else:
            lastName = name.split(" ")[-1]
        # semantic analysis
        for checkName in uniqueNamesAtAddress:
            if (name == checkName):
                continue
            splitName = checkName.split(" ")
            if ("III" in checkName or "II" in checkName or "1" in checkName or "2" in checkName):
                checkLastName = checkName.split(" ")[-2]
            else:
                checkLastName = checkName.split(" ")[-1]
            if semanticNameCheck(lastName, checkLastName, SEMANTIC_SIM_THRESHOLD):
                # now let's check the first names
                firstName = name.split(" ")[0]
                firstCheckName = checkName.split(" ")[0]
                if semanticNameCheck(firstName, firstCheckName, SEMANTIC_SIM_THRESHOLD):
                    # we have an alias
                    existingAliases = set()
                    if name in aliases.keys():
                        existingAliases = aliases[name]
                    else:
                        existingAliases = {name}
                    existingAliases.add(checkName)
                    aliases[name] = existingAliases
                else:
                    if(not isKnownAlias(name, household)):
                        existingHousehold = set()
                        if name in household.keys():
                            existingHousehold = household[name]
                        else:
                            existingHousehold = {name}
                        existingHousehold.add(checkName)
                        household[name] = existingHousehold

formattedAliases = dict.fromkeys(aliases.keys())
print("****aliases***")
for primaryName in aliases.keys():
    formattedAliases[primaryName] = list(aliases[primaryName])
    print("for " + primaryName)
    for alias in aliases[primaryName]:
        print(alias)

with open(aliasFile, "w") as outfile:
    json.dump(formattedAliases, outfile)

print("****households***")
for householdKey in household.keys():
    print("shared household: " + householdKey)
    for shared in household[householdKey]:
        print(shared)


"""
Retry the household bullshit but this time with an emphasis on straw donor identification

in scope:
all individuals at the address with unique names
include married couple donations

eventually we'll take last names into account
"""

addressNames = dict.fromkeys(str(uniqueAddresses), [])
for addy in uniqueAddresses:
    addyDF = contributorDF[contributorDF["Street "] == addy]
    uniqueNamesAtAddress = addyDF['Upper Combined Names'].unique().tolist()
    if (len(uniqueNamesAtAddress) > 2):
        print(addy)
        print(*uniqueNamesAtAddress)
        print("*********")
    addressNames[str(addy)] = uniqueNamesAtAddress

with open(householdFile, "w") as outfile:
    json.dump(addressNames, outfile)