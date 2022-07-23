"""

bugs:
w vs west --- it's why we aren't catching the david spence phenomenon
    - let's clean all the addresses( street vs st., e vs east, 8th vs eighth, etc)

let's make sure the SPOUSE and SPOUSE is catching each as an alias.
    - EX ALIAS DICT: {mark schlosser: [christie schlosser, christie and mark schlosser, mark schlosser]}

"""


from prettytable import PrettyTable
from statistics import mean, multimode, quantiles
import pandas as pd
import sys, numpy, spacy

numpy.set_printoptions(threshold=sys.maxsize)
nlp = spacy.load("en_core_web_lg")
pd.options.display.max_columns = None

contributorsDoc = "Campaign_Finance (2).xlsx"

appointeeDoc = "Appointee to Council Donations (No Duplicates).xlsx"

illegalDoc = open("IllegalActions.txt","w")

suspiciousDoc = open("SuspiciousActions.txt", "w")

appointeeDF = pd.read_excel(appointeeDoc, index_col=0)

SEMANTIC_SIM_THRESHOLD = 0.73


financeDF = pd.read_excel(contributorsDoc)

mayor = 'Eric Johnson'

councilMembers = ['Eric Johnson', 'Chad West', "Jesus Moreno", "Casey Thomas", "Carolyn KIng Arnold", "Carolyn Arnold", "carolyn arnold", "Jaime Resendez", "Omar Narvaez", "Adam Bazaldua", "Tennell Atkins", "Paula Blackmon", "Byron McGough", "Jaynie Schultz", "Cara Mendelsohn", "Gay Willis", "Paul Ridley"]

head = ["Councilperson", "Total Contributions", "sum of loans", "Num Contributions", "Num Unique Contributors", "Avg Contribution", "Total Expenditures", "Remaining Funds", "Out of District Contributions", "% of OoD Contributions to Total Contributions", "25% Quantile", "50% Quantile", "75% Quantile"]
outputTable = PrettyTable(head)

#OoS = out of state
outofStateHead = ["Councilperson", "Total OoS contributions", "Num OoS Unique Contributors", "Avg OoS Contribution"]
outofStateTable = PrettyTable(outofStateHead)
redFlagTable = PrettyTable()
cutoff = {}

# Zipcode Analysis
tempDF = pd.read_excel(contributorsDoc)
zipsDF = tempDF.loc[(tempDF['Contact Type'] == "Contributor")]

allzipcodes = zipsDF.Zipcode.unique().tolist()
uniquerZips = set()
# clean the zipcodes - remove all -xxxx suffixes
for zip in allzipcodes:
    if isinstance(zip, str):
        allzipcodes.remove(zip)
        uniquerZips.add(float(zip.split("-")[0]))
    else:
        uniquerZips.add(zip)

print("uniquer zips: ",len(uniquerZips))

dallasZips = [75201, 75202, 75203, 75204, 75206, 75207, 75208, 75210, 75211, 75212, 75214, 75215, 75216, 75217, 75218, 75220, 75221, 75222, 75223, 75224, 75226 ,75227 ,75228, 75229, 75230, 75231, 75232, 75233, 75235, 75236, 75237, 75238, 75240, 75241, 75242, 75243, 75244, 75246, 75247, 75248, 75249, 75250, 75251, 75252, 75253, 75254, 75260, 75261, 75262, 75263, 75264, 75265, 75266, 75267 ,75270, 75277, 75285, 75287, 75301, 75303, 75312, 75313, 75315, 75320, 75326, 75336, 75339, 75342, 75354, 75355, 75356, 75357, 75358, 75359, 75360, 75367, 75368, 75370, 75371, 75372, 75373, 75374, 75376, 75378, 75379, 75380, 75381 ,75382, 75389, 75390 ,75392, 75393, 75394, 75395, 75397, 75398]
parkCitiesZips = [75205, 75209, 75219, 75225,75275, 75283, 75284, 75391]
outsideZips = list(filter(lambda i: i not in dallasZips, uniquerZips))

# property map - https://maps.dcad.org/prd/dpm/

contributionsByZip = dict.fromkeys(uniquerZips, 0)

for zip in allzipcodes:
    zipContributions = sum(zipsDF.loc[zipsDF['Zipcode'] == zip].Amount.values.tolist())
    if isinstance(zip, str):
        cleanedZip = float(zip.split("-")[0])
    else:
        cleanedZip = zip
    if cleanedZip in contributionsByZip.keys():
        contributionsByZip[cleanedZip] = contributionsByZip[cleanedZip] + zipContributions
    else:
        contributionsByZip[cleanedZip] = zipContributions


topContributorsSum = 0

print("top contributing zipcodes:")
for zip in sorted(contributionsByZip, key=contributionsByZip.get, reverse=True)[:5]:
    print(zip, round(contributionsByZip[zip]))
    topContributorsSum+=contributionsByZip[zip]


# verify total contributions from all zipcodes match total contributions in whole dataframe
fullDF = pd.read_excel(contributorsDoc)
fullDF = fullDF.loc[(fullDF['Contact Type'] == "Contributor")]
allContributionsSum = round(sum(fullDF.Amount.values.tolist()),2)


print("total num zips: ")
print(len(uniquerZips))
print("top 5 zipcodes contributed: ")
print(round(topContributorsSum))
print("% of all contributions: ")
print(round(topContributorsSum/allContributionsSum*100,2))

print("total contributions made to any candidate")
print(allContributionsSum)

parkCitiesContributions = 0
for zip in parkCitiesZips:
    if zip in contributionsByZip.keys():
        parkCitiesContributions+=contributionsByZip[zip]

print("contributions from zips in park cities (non-dallas): ")
print(round(parkCitiesContributions,2))

print("% of total contributions from park cities: ")
print(round(parkCitiesContributions/allContributionsSum*100,2))


outsideContributions = 0
for zip in outsideZips:
    outsideContributions += contributionsByZip[zip]

print("total outside contributions")
print(round(outsideContributions,2))

print("% of total contributions from outside zips")
print(round(outsideContributions/allContributionsSum*100,2))








# address analysis

print("--------begin address analysis---------")
anotherDF = pd.read_excel(contributorsDoc)
addressDF = anotherDF.loc[(anotherDF['Contact Type'] == "Contributor")]

allAddresses = addressDF["Geo Location"].unique().tolist()

# clean the addresses - remove all -xxxx suffixes
uniqueAddresses = set(allAddresses)

contributionsByAddy = {}

for zip in uniqueAddresses:
    addressContributions = sum(zipsDF.loc[addressDF['Geo Location'] == zip].Amount.values.tolist())
    if zip in contributionsByAddy.keys():
        contributionsByAddy[zip] = round(contributionsByAddy[zip] + addressContributions,2)
    else:
        contributionsByAddy[zip] = addressContributions

topContributorsSum = 0

print("top contributing addresses:")
for zip in sorted(contributionsByAddy, key=contributionsByAddy.get, reverse=True)[:5]:
    print("-----")
    topContributorsSum+=round(contributionsByAddy[zip],2)
    lastNamesAtAddy = set(zipsDF.loc[addressDF['Geo Location'] == zip]['Last Name'].values.tolist())
    combinedNamesAtAddy = set(zipsDF.loc[addressDF['Geo Location'] == zip]['Upper Combined Names'].values.tolist())
    print(zip, round(contributionsByAddy[zip],2), len(combinedNamesAtAddy), len(lastNamesAtAddy))

spread = [round(q, 1) for q in quantiles(contributionsByAddy.values(), n=10)]

print("total contributions made by these top addresses")

print(topContributorsSum)

print(spread)


print("--------end address analysis---------")


# get a set of unique addresses - unique and set may be redundant, but just to be safe
uniqueAddresses = set(financeDF["Street "].unique().tolist())

def semanticNameCheck(name1, name2, threshold):
    """
    # checks for Christopher vs Chris - only if we need it
    if (name1 in name2 or name2 in name1):
        return true
    """

    name1_doc = nlp(name1)
    name2_doc = nlp(name2)
    sim = name1_doc.similarity(name2_doc)
    if sim > threshold:
        return True
    return False



"""
what do we want?
1. all contributions at an address where the last names match
2. all contributions at an address where the first and last names match
3. all contributions at an address to any council member mayor

* we want this to work for semantic similarity
"""


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
    # 1. all contributions at an address where the last names match


        #familyContributionsAtAddress[lastName] += sum(addyDF[addyDF['Last Name'] == lastName].Amount.values.tolist())
        # write each family contribution at address to suspicious file



# for each councilmember
for name in councilMembers:
    # build dataframe of their finances
    councilpersonDF = financeDF.loc[financeDF['Candidate Name'] == name]
    copyDF = councilpersonDF
    anotherCopyDF = copyDF

    # build dataframe of contributions
    contributionsDF = councilpersonDF.loc[(councilpersonDF['Contact Type'] == "Contributor")]
    zipContributionsDF = contributionsDF
    totalContributions = contributionsDF.Amount.values.tolist()

    # build dataframe of expenditures
    expendituresDF = copyDF.loc[copyDF['Contact Type'] == "Expenditure"]
    totalExpenditures = expendituresDF.Amount.values.tolist()
    sumExpenditures = round(sum(totalExpenditures), 0)

    # build dataframe of loans
    lendersDF = anotherCopyDF.loc[(anotherCopyDF['Contact Type'] == 'Lender')]
    totalLoans = lendersDF.Amount.values.tolist()
    sumLoans = sum(totalLoans)

    # MultiMode
    multiMode = multimode(totalContributions)

    # Total Contributions
    sumContributions = round(sum(totalContributions), 0)

    # Get number of contributions
    numContributions = len(totalContributions)

    # Get number of unique contributors
    uniqueContributors = set()
    uniqueContributors.update(contributionsDF["Upper Combined Names"].values.tolist())

    # Get avg contribution per contributor
    avgContributions = round(sum(totalContributions)/len(uniqueContributors), 2)

    # get remainder of campaign funds
    remainingFunds = sumContributions - sumExpenditures

    # Get Out of Dallas Contributors
    outofDistrict = zipContributionsDF[zipContributionsDF['Zipcode'].isin(outsideZips)]
    outofDistrictContributions = outofDistrict.Amount.values.tolist()

    # Get out of state avg contributions
    outOfStateDF = contributionsDF.loc[contributionsDF['State'] != 'TX']
    outOfStateContributions = outOfStateDF.Amount.values.tolist()

    namesOutOfState = outOfStateDF[outOfStateDF['Amount'] > 500]['Combined Names'].values.tolist()


    print("out of state donations exceeding $500 for ", name)
    for donor in namesOutOfState:
        print(donor)

    outOfStateAvgContributions = 0
    outofStateSumContributions = 0
    outOfStatenumContributions = 0

    outofStateUniqueContributors = set()
    outofStateUniqueContributors.update(outOfStateDF["Upper Combined Names"].values.tolist())

    if len(outOfStateContributions) > 0:

        outofStateSumContributions = round(sum(outOfStateContributions), 2)

        outOfStateAvgContributions = round(outofStateSumContributions/len(outofStateUniqueContributors),2)

        # Get number of unique out of state contributors
        outOfStatenumContributions = len(outOfStateContributions)

    spread = [round(q, 1) for q in quantiles(totalContributions, n=4)]


    cutoff[name] = spread[2]


    outputTable.add_row([name, sumContributions, sumLoans, numContributions, len(uniqueContributors), avgContributions, sumExpenditures, remainingFunds, round(sum(outofDistrictContributions),2), round(sum(outofDistrictContributions)/sumContributions*100), spread[0], spread[1], spread[2]])
    outofStateTable.add_row([name, outofStateSumContributions, len(outofStateUniqueContributors), outOfStateAvgContributions])

print(outputTable)

print(outofStateTable)

sleezebags = set()
print("these are all the appointees who were in the top 25% of contributors for each council-member")
for c in cutoff.keys():
    if(c in appointeeDF.columns):
        redflags = appointeeDF.loc[appointeeDF[c] >= cutoff[c]]
        print(c, *redflags.index)
        sleezebags.update(redflags.index)

print("these appointees were in the top 25% of contributors to any councilmember")
print(sleezebags)




illegalDoc.close()

# unique contributors from park cities

# councilmembers receiving most from park cities
