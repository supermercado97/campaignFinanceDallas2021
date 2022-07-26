"""
rulebook:
https://codelibrary.amlegal.com/codes/dallas/latest/dallas_tx/0-0-0-6263

resolved bugs
- timothy byrne is missing from aliases but is found in shared household
- rita sue gold doesn't find rita gold as alias
- tim and melanie byrne donation to cara mendelson not found
- nancy best donated $2000 to bazaldua but didn't get picked up by the software
    -- this is bc she doesn't have an alias.
    -- we'll need to analyze everybody who doesn't have an alias

unresolved tasks
-

resolved tasks
1. look at how much each alias donated to each candidate
2. If the total contributions exceeds alotted amount ($5000 for mayor, $1000 for council member) write to document
    - name of donor
    - aliases used
    - amount each alias donated to the council member
    - total contribution to the council member
3. write aliases to a doc in a different file
4. load the aliases from a doc in this file
5. Look at household donations to search for straw donations

"""
from prettytable import PrettyTable
from statistics import mean, multimode, quantiles
import pandas as pd
import sys, numpy, spacy, json

# define external library parameters
numpy.set_printoptions(threshold=sys.maxsize)
nlp = spacy.load("en_core_web_lg")
pd.options.display.max_columns = None

# set variable defs and output files
aliasFile = 'DonorAliases.json'
contributorsDoc = "Campaign_Finance (2).xlsx"
mayor = 'Eric Johnson'
maxDonationMayor = 5000
maxDonationCouncil = 1000
SEMANTIC_SIM_THRESHOLD = 0.73

# open files and load data
illegalDoc = open("IllegalActions.txt","w")
financeDF = pd.read_excel(contributorsDoc)
contributorDF = financeDF.loc[(financeDF['Contact Type'] == "Contributor")]
uniqueAddresses = set(financeDF["Street "].unique().tolist())

# load aliases from file
f = open(aliasFile)
aliases = json.load(f)
f.close()

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

def isCouple(name):
    return ("&" in name) or ('AND' in name)

# header in output file
illegalDoc.write("********* Donations from Aliases and Married Couples *********")

# begin alias contribution analysis
allUniqueCandidates = set(contributorDF["Candidate Name"].unique().tolist())

"""

primaryName - defined as legal name, not an alias (key in alias dict)
"""
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

    # look for illegal donations - donations above campaign contribution limits
    for candidate in primaryNameContributions.keys():
        if(primaryNameContributions[candidate] > maxDonation(candidate)):
            sharedName = "".join(s for s in aliases[primaryName] if "AND" in s)
            if (not sharedName):
                sharedName = "".join(s for s in aliases[primaryName] if "&" in s)
            illegalDoc.write("**********\n")
            for alias in aliasDonationsToCandidate.keys():
                tempAlias = aliasDonationsToCandidate[alias]

                if(candidate in tempAlias.keys()):
                    illegalDoc.write(alias + "\t\t\t\t" + "$" + str(aliasDonationsToCandidate[alias][candidate]) + "\t\t\t\t" + candidate + "\n")


            # replace below with writeFunc that takes in a name
            if (sharedName):
                illegalDoc.write(sharedName + " total contributions to " + "\t\t\t\t" + candidate + "\t\t\t\t" + " $" + str(primaryNameContributions[candidate]) + "\n")
            else:
                illegalDoc.write(primaryName + " total contributions to " + "\t\t\t\t" + candidate + "\t\t\t\t" + " $" + str(primaryNameContributions[candidate]) + "\n")


# let's take a look at donors who are not using aliases
# this does not include donations from businesses
illegalDoc.write("********* Donations from Individuals (no aliases used) *********\n")
uniqueNames = set(contributorDF['Upper Combined Names'].unique().tolist())
for name in uniqueNames:
    if isKnownAlias(name, aliases) or name == " ":
        continue
    donorDF = contributorDF[contributorDF['Upper Combined Names'] == name]
    for candidate in allUniqueCandidates:
        donorContributionsToCandidate = sum(donorDF[donorDF['Candidate Name'] == candidate].Amount.values.tolist())
        donationThreshold = maxDonation(candidate) if not isCouple(name) else 2*maxDonation(candidate)
        if donorContributionsToCandidate > donationThreshold:
            illegalDoc.write(name + "\t\t\t\t" + " total contributions to " + "\t\t\t\t" + candidate + "\t\t\t\t" + " $" + str(donorContributionsToCandidate) + "\n")

illegalDoc.close()