"""

bugs
- timothy byrne is missing from aliases but is found in shared household
- rita sue gold doesn't find rita gold as alias
- tim and melanie byrne donation to cara mendelson not found
next steps:
1. look at how much each alias donated to each candidate
2. If the total contributions exceeds alotted amount ($5000 for mayor, $1000 for council member) write to document
    - name of donor
    - aliases used
    - amount each alias donated to the council member
    - total contribution to the council member
3. write aliases to a doc in a different file
4. load the aliases from a doc in this file
"""
from prettytable import PrettyTable
from statistics import mean, multimode, quantiles
import pandas as pd
import sys, numpy, spacy

numpy.set_printoptions(threshold=sys.maxsize)
nlp = spacy.load("en_core_web_lg")
pd.options.display.max_columns = None

contributorsDoc = "Campaign_Finance (2).xlsx"
financeDF = pd.read_excel(contributorsDoc)
illegalDoc = open("IllegalActions.txt","w")
SEMANTIC_SIM_THRESHOLD = 0.73

mayor = 'Eric Johnson'
councilMembers = ['Eric Johnson', 'Chad West', "Jesus Moreno", "Casey Thomas", "Carolyn KIng Arnold", "Carolyn Arnold", "carolyn arnold", "Jaime Resendez", "Omar Narvaez", "Adam Bazaldua", "Tennell Atkins", "Paula Blackmon", "Byron McGough", "Jaynie Schultz", "Cara Mendelsohn", "Gay Willis", "Paul Ridley"]

maxDonationMayor = 5000
maxDonationCouncil = 1000

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

def maxDonation(candidate):
    if(candidate == mayor):
        return maxDonationMayor
    return maxDonationCouncil

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
print("****aliases***")
for aliasKey in aliases.keys():
    print("for " + aliasKey)
    for alias in aliases[aliasKey]:
        print(alias)

print("****households***")
for householdKey in household.keys():
    print("shared household: " + householdKey)
    for shared in household[householdKey]:
        print(shared)

# begin alias contribution analysis
allUniqueCandidates = set(contributorDF["Candidate Name"].unique().tolist())
for primaryName in aliases.keys():
    primaryNameContributions = dict.fromkeys(allUniqueCandidates, 0)
    aliasDonationsToCandidate = dict.fromkeys(aliases[primaryName], {})
    for alias in aliases[primaryName]:
        totalAliasContributionsToCandidate = 0
        if("&" in alias or "AND" in alias):
            spouse = alias.split("&")[-1].split("AND")[-1][1:]
            spouseDF = contributorDF[contributorDF["Upper Combined Names"] == spouse]
            uniqueCandidates = set(spouseDF["Candidate Name"].unique().tolist())
            aliasDonationsToCandidate[spouse] = {}
            for candidate in uniqueCandidates:
                totalAliasContributionsToCandidate = round(sum(spouseDF[spouseDF['Candidate Name'] == candidate].Amount.values.tolist()), 2)
                primaryNameContributions[candidate] = primaryNameContributions[candidate] + totalAliasContributionsToCandidate
                aliasDonationsToCandidate[spouse][candidate] = totalAliasContributionsToCandidate

        donorDF = contributorDF[contributorDF["Upper Combined Names"] == alias]
        uniqueCandidates = set(donorDF["Candidate Name"].unique().tolist())
        tempDict = dict.fromkeys(uniqueCandidates, 0)
        for candidate in uniqueCandidates:
            totalAliasContributionsToCandidate = round(sum(donorDF[donorDF['Candidate Name'] == candidate].Amount.values.tolist()),2)
            primaryNameContributions[candidate] = primaryNameContributions[candidate] + totalAliasContributionsToCandidate
            tempDict[candidate] = totalAliasContributionsToCandidate
        aliasDonationsToCandidate[alias] = tempDict

    # look for illegal donations
    for candidate in primaryNameContributions.keys():
        if(primaryNameContributions[candidate] > maxDonation(candidate)):
            print("**********")
            illegalDoc.write("**********\n")
            for alias in aliasDonationsToCandidate.keys():
                tempAlias = aliasDonationsToCandidate[alias]

                if(candidate in tempAlias.keys()):
                    print(alias + "\t\t\t\t" + "$" + str(tempAlias[candidate]) + "\t\t\t\t" + candidate)
                    illegalDoc.write(alias + "\t\t\t\t" + "$" + str(aliasDonationsToCandidate[alias][candidate]) + "\t\t\t\t" + candidate + "\n")
            sharedName = "".join(s for s in aliases[primaryName] if "AND" in s)
            if (not sharedName):
                sharedName = "".join(s for s in aliases[primaryName] if "&" in s)

            # replace below with writeFunc that takes in a name
            if (sharedName):
                print(sharedName + " total contributions to " + candidate + " $" + str(primaryNameContributions[candidate]))
                illegalDoc.write(sharedName + " total contributions to " + candidate + " $" + str(primaryNameContributions[candidate]) + "\n")
            else:
                print(primaryName + " total contributions to " + candidate + " $" + str(primaryNameContributions[candidate]))
                illegalDoc.write(primaryName + " total contributions to " + candidate + " $" + str(primaryNameContributions[candidate]) + "\n")

# now do individual contribution analysis
# we want to gather how much each individual donated to any candidate
illegalDoc.close()