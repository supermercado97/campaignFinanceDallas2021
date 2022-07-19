"""

Look at out-of-state contributions per council-member
Look at avg donations per council-member

total contributions to successful campaigns (including mayor) - 2,075,754
excluding mayor - $1,800,860

total out of dallas contributions (incl mayor) - $819,959
excl mayor - $690,591
Suggested Features
- Determine the number of unique contributors to a campaign
- Total loans to each candidate
- How many candidates lost and were outspent
- look through the city council meetings for instances where people who donated later showed up in the agendas
    - initial search via appointees list
    - search for addresses referenced in city minutes
- Look into applying for or suggesting one of our mutual aid friends apply for a board position
    - Community Development Commission ***fund community programs babyyyy***
        resendez
    - Citizen Homelessness Commission (CHC)  ***literally anybody in our spaces***
        resendez
        blewett
    - Community Police Oversight Board ***ideal for the folks with white privilege ***
    - Dallas Area Partnership To End And Prevent Homelessness Local Government Corporation
        fake ass corporation requires real estate, philanthropic, housing authority, and VA reps
    - Environmental Commission ***underlooked position with possibility for major plays***
        thomas
        arnold
        atkins
        mcgough
    - Ethics Advisory Commission ***interesting option***
        no vacancies.
        ***note that pam gerber donated a total of $3,350 to councilmembers and lives in park cities***
    - Housing Finance Corporation *** many vacancies***
        moreno
        resendez
        bazaldua
    - Martin Luther King Jr Community Center Board *** direct area of impact concerning SWC work***
        arnold
        bazaldua
        atkins
Interesting Findings:
Only 2/14 Councilmembers took out loans to fund their campaign. Many of their competitors DID take out loans.
Mean > Median in all cases of campaign contributions for councilmembers
Tennel Atkins had the fewest small-donation contributions
7/14 Councilmembers had 25% of contributions being over $1000
Jaynie Schultz and Chad West spent the most on their campaigns among elected councilmembers.

B

"""


from prettytable import PrettyTable
from statistics import mean, multimode, quantiles
import pandas as pd
import sys
import numpy

numpy.set_printoptions(threshold=sys.maxsize)

pd.options.display.max_columns = None

contributorsDoc = "Campaign_Finance (1).xlsx"

appointeeDoc = "Appointee to Council Donations (No Duplicates).xlsx"
appointeeDF = pd.read_excel(appointeeDoc, index_col=0)


financeDF = pd.read_excel(contributorsDoc)

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
uniquerZips = []
# clean the zipcodes - remove all -xxxx suffixes
for zip in allzipcodes:
    if isinstance(zip, str):
        allzipcodes.remove(zip)
        uniquerZips.append(float(zip.split("-")[0]))
    else:
        uniquerZips.append(zip)

print("uniquer zips: ",len(uniquerZips))

dallasZips = [75201, 75202, 75203, 75204, 75206, 75207, 75208, 75210, 75211, 75212, 75214, 75215, 75216, 75217, 75218, 75220, 75221, 75222, 75223, 75224, 75226 ,75227 ,75228, 75229, 75230, 75231, 75232, 75233, 75235, 75236, 75237, 75238, 75240, 75241, 75242, 75243, 75244, 75246, 75247, 75248, 75249, 75250, 75251, 75252, 75253, 75254, 75260, 75261, 75262, 75263, 75264, 75265, 75266, 75267 ,75270, 75277, 75285, 75287, 75301, 75303, 75312, 75313, 75315, 75320, 75326, 75336, 75339, 75342, 75354, 75355, 75356, 75357, 75358, 75359, 75360, 75367, 75368, 75370, 75371, 75372, 75373, 75374, 75376, 75378, 75379, 75380, 75381 ,75382, 75389, 75390 ,75392, 75393, 75394, 75395, 75397, 75398]
parkCitiesZips = [75205, 75209, 75219, 75225,75275, 75283, 75284, 75391]
outsideZips = list(filter(lambda i: i not in dallasZips, uniquerZips))

# property map - https://maps.dcad.org/prd/dpm/

"""
suspicious properties
https://montgomerystreetpartners.com/contact/ - 75219 donated to many campaigns
3953 Maple ave
lamont also owns
https://opencorporates.com/companies/us_tx/0059618000
https://www.fastpeoplesearch.com/max-lamont_id_G7459552138962769448


doug deason
https://twitter.com/dougdeason
3953 Maple ave
son of https://en.wikipedia.org/wiki/Darwin_Deason - billionare


https://www.sos.state.tx.us/corp/managementinfofaqs.shtml#mgmt7
SoS doesn't keep track of LLC ownership
https://www.ethics.state.tx.us/resources/FAQs/2020election_faqs.php#Q11
says LLC with corp owner can't make contributions


https://opencorporates.com/companies/us_tx/0800936298
LPC Retail LLC
PO Box 1920 - Donations made by the POUGE family
Dallas, TX 75221 8000.0 4 2
owned by a corporation: C T Corporation System
https://opencorporates.com/companies/us_tx/0001410606
this is apparently not allowed by state ethics commission
CT Corporation Systems has a president named john weber - whose wife angela and he have donated A LOT of money in this campaign
delores pouge - https://www.spokeo.com/Jean-Pogue/Texas/Dallas/p269654771
mack pouge - former partner of trammel crow

these are the families that run dallas.^

for po box 117540
owned by james tatum
gandolf15**@aol.com
might have affiliations with amy jean espaza - https://www.truepeoplesearch.com/find/person/p9lr9nr2n4rn02l9n9un
according to https://www.locatepeople.org/james-tatum/
james should have had this PO for 15+ years


!!!!!!!look at harlan crow, son of trammel crow, whose company by his namesake is affiliated to Don WILLIAMS (8604 greenville ave)!!!!!

po box 17428 affiliated with this company - https://opencorporates.com/companies/us_tx/0163725500
robert haass
richard c haass
also affiliated with https://profiles.superlawyers.com/texas/austin/lawfirm/linebarger-goggan-blair-and-sampson-llp/fb9e6c94-ca36-4a63-aca0-ef39cbd911bd.html
    -MADRID MCLAUGHLIN POST 10354 VETERANS OF FOREIGN WARS
also affiliated with https://opencorporates.com/companies/us_tx/0030444001
    -MADRID MCLAUGHLIN POST 10354 VETERANS OF FOREIGN WARS 

po box 803447
https://opencorporates.com/companies/us_tx?action=search_companies&branch=&commit=Go&controller=searches&inactive=false&mode=best_fields&nonprofit=&order=&q=PO+Box+803447&search_fields%5B%5D=name&search_fields%5B%5D=previous_names&search_fields%5B%5D=company_number&search_fields%5B%5D=other_company_numbers&search_fields%5B%5D=registered_address_in_full&utf8=%E2%9C%93

half of the top contributing addresses come from Park Cities Zip Codes

Looking closer than just zipcodes, we find that there are several addresses that not only donate in the highest bracket of campaign contributions, but also have several names associated.

Analysis shows that ther can be multiple donations under the same last name, but that are offered under different first names. This alone wouldn't be cause for alarm, but amidst these we find additional layers of obscurity among the highest campaign contributions.

Among PO Boxes, it's difficult to identify with any particular owner, but the amount donated sits well above the top 75% of contributions. Without the ability to identify which individual is associated with these contributions, we'll resort to analyzing the affiliated businesses.

As we have done with the majority of addresses, we're looking at the owners of these properties to identify the individuals responsible for funding these campaigns.

Further, since 10/20 of the top contributing addresses reside outside of Dallas City Council Districts, it's worth noting that the two candidates who received the highest amounts of out of state contributinons also received the greatest amount of out-of-district contributions

Chad West and Jaynie Schultz received $99,123 and $82,030 respectively. In other words, 34% of Chad West's campaign and 30% of Jaynie Schultz' campaign contributions came from out-of-district donors.

use quartiles to map how much in district vs out of district in each segment


new questions:
1. what percent of winning campaigns received donations from park cities
2. are the total contributions getting calculated correctly 
3. can we build a zipcode map by contributions
4. can we get a list of the following:
    - names of individuals/businesses making out-of-state donations (to who and how much)
    - names of individuals/businesses makign out-of-district donations (to who and how much)
    - names of individuals trying to hide their donations amounts
        - using aliases - same address, same last name
        - using the names of others in their household - same address, same last name

BART BEVERS - Dallas Inspector General Office
ext 6704880
hiring qualifications
- ex fraud investigator background
- ex police investigator background

Dallas Campaign Finance Contributions Code Violations
0. $5,000 cap on contributions to mayoral races
1. 15A-2 individuals and certain businesses may not make more than $1000 in donations to a single candidate
2. 15A-5 Use of legal name
3. donations from out-of-state commitees totalling more than $500 must report all donors who gave more than  $100 to the out-of-state committee in the last 12 months
** (b)  This section does not apply to a contribution from an out-of-state political committee if the committee appointed a campaign treasurer under Chapter 252 before the contribution was made and is subject to the reporting requirements of Chapter 254.**

"""

contributionsByZip = dict.fromkeys(outsideZips, 0)


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
allZipContributions = sum(contributionsByZip.values())

print("total num zips: ")
print(len(uniquerZips))
print("top 5 zipcodes contributed: ")
print(round(topContributorsSum))
print("% of all contributions: ")
print(round(topContributorsSum/allZipContributions*100,2))

print("total contributions made to any candidate")
print(allZipContributions)

parkCitiesContributions = 0
for zip in parkCitiesZips:
    if zip in contributionsByZip.keys():
        parkCitiesContributions+=contributionsByZip[zip]

print("contributions from zips in park cities (non-dallas): ")
print(round(parkCitiesContributions,2))

print("% of total contributions from park cities: ")
print(round(parkCitiesContributions/allZipContributions*100,2))


outsideContributions = 0
for zip in outsideZips:
    outsideContributions += contributionsByZip[zip]

print("total outside contributions")
print(round(outsideContributions,2))

print("% of total contributions from outside zips")
print(round(outsideContributions/allZipContributions*100,2))





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
for zip in sorted(contributionsByAddy, key=contributionsByAddy.get, reverse=True)[:40]:
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






# unique contributors from park cities

# councilmembers receiving most from park cities
