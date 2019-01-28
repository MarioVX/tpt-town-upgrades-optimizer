'''
The Perfect Tower - Town Upgrades Optimizer
game by XmmmX99 & SpeedyBrain
found here: https://www.kongregate.com/games/XmmmX99/the-perfect-tower
script by MarioVX
Version 1.0

This script for the game "The Perfect Tower" calculates optimal Town Credits allocations
to maximize effective Town Credit income rate during your next Town Tier.
The only upgrades compared explicitly are those with inambiguously quantifiable benefit to TC income:
   * Conversion Rate from BPT to TC
   * Special Resource Drop Rate bonus per unspent TC
   * Statistics Bonus Increase.
The benefit of all other Town Upgrades depends on a fair amount of assumptions and can vary.
Therefore, the script also contains functions to check the opportunity cost of a different upgrade,
and allow the user to guess himself whether it is worth it or not.
For a specific benefit assumption, the script can also search for the TC amount at which this becomes worth it.
Special version for the Speed upgrades included so users don't have to bother with the benefit calculation.
'''

from math import floor

#(starting cost, growth rate, max level) for all Town Upgrades.
costparameters = {
    "cr":(5,1.65,10),
    "dr":(2,1.6,20),
    "sb":(5,1.9,8),
    "sp":(1000,100,2),
    "uts":(5,1.8,10),
    "gc":(50,1.5,5),
    "uls":(25,1.9,2),
    "fg":(375,1,1)}

def Cost(upgrade,current,target):
    '''
    Calculate the cumulative town credit cost of raising a specific town upgrade from current to target level.
    upgrade parameter uses the keys from costparameters.
    '''
    total = 0
    for l in range(current,target):
        total += floor(costparameters[upgrade][0]*costparameters[upgrade][1]**l)
    return total

def findbest(credits, enemytier, basestatbonus, conversionratelvl, dropratelvl, statbonuslvl):
    '''
    For the configuration specified by the arguments, returns the optimal TC allocation post-TT.
    Assumes Conversion Rate upgrades to be bought at the end of the next TT.
    Only Conversion Rate, Drop Rate & Statistics Bonus are considered.
    
    Args:
        credits (int): Number of credits available for spending on the upcoming TT.
        enemytier (int): 0 if you'll still be able to bring ET up to your BPT, 1 if your BPT will outgrow it.
        basestatbonus (int): the *base* statistics bonus to presuppose in the comparison as percentage points, e.g. 640 for the max of 640%.
        conversionratelvl (int): current level of your BPT to TC Conversion Rate town upgrade.
        dropratelvl (int): current level of your SR Drop Rate per unspent TC town upgrade.
        statbonuslvl (int): current level of your Bonus from Statistics Goals increase town upgrade.
    
    Returns:
        tuple: ((cr,dr,sb),mult) with the optimal levels of conversion rate, drop rate and stat bonus, and multiplier over no TUs.
    
    '''
    ma = 0
    argma = tuple()
    for cr in range(conversionratelvl, 11):
        for dr in range(dropratelvl, 21):
            for sb in range(statbonuslvl, 9):
                cost = Cost("cr",conversionratelvl,cr) + Cost("dr",dropratelvl,dr) + Cost("sb",statbonuslvl,sb)
                if cost <= credits:
                    val = (5+11*cr)**(1+enemytier) * (1000+dr*(credits-cost+Cost("cr",conversionratelvl,cr))) * (800+basestatbonus * (8+sb))
                    arg = (cr,dr,sb)
                    if val>ma:
                        argma = arg
                        ma = val
                    # tie-breaking
                    elif val==ma:
                        if cost < Cost("cr",conversionratelvl,argma[0])+Cost("dr",dropratelvl,argma[1])+Cost("sb",statbonuslvl,argma[2]):
                            argma = arg
                        elif cost == Cost("cr",conversionratelvl,argma[0])+Cost("dr",dropratelvl,argma[1])+Cost("sb",statbonuslvl,argma[2]):
                            if arg[1]*(credits-cost+Cost("cr",conversionratelvl,cr)) > argma[1]*(credits-Cost("dr",dropratelvl,argma[1])-Cost("sb",statbonuslvl,argma[2])):
                                argma = arg
                            elif arg[1]*(credits-cost+Cost("cr",conversionratelvl,cr)) == argma[1]*(credits-Cost("dr",dropratelvl,argma[1])-Cost("sb",statbonuslvl,argma[2])):
                                if arg[0]<argma[0]:
                                    argma = arg
                                elif arg[0]==argma[0]:
                                    print("Unhandled Tie Break!")
    return (argma,ma/1000/5**(1+ enemytier)/(800+ basestatbonus * 8))

def listall(enemytier, basestatbonus, cr, dr, sb):
    '''
    For the specified configuration, creates a sorted list of optimal TC allocations for all TC amounts.
    List entries are (credits, (cr,dr,sb)), with credits being the first TC number at which the allocation
     becomes optimal, remaining up to the next entry.
    '''
    result = []
    creds = 1
    last = (cr,dr,sb)
    while last != (10,20,8):
        new = findbest(creds,enemytier,basestatbonus,cr,dr,sb)
        if new[0] != last:
            result.append((creds,new[0],new[1]))
            print(creds,new)
        creds += 1
        last = new
    return result

def opportunitycost(upgradecost, credits, enemytier, basestatbonus, cr, dr, sb):
    '''
    Calculates the SR income multiplier equivalent you are missing out on if you buy an upgrade
    of the specified cost at your current state.
    '''
    if upgradecost>credits:
        return "Invalid Input! Must have at least as many credits as the upgrade costs."
    multwithup = findbest(credits-upgradecost,enemytier,basestatbonus,cr,dr,sb)[1]
    multwithoutup = findbest(credits,enemytier,basestatbonus,cr,dr,sb)[1]
    return multwithoutup/multwithup

def findbreakeven(upgradecost,upgrademult,enemytier,basestatbonus,cr,dr,sb):
    '''
    Calculates the amount of TC you need for a specified upgrade to break even.
    
    Args:
        upgradecost (int): Cost of the upgrade in question.
        upgrademult (float): Estimated effective multiplier this upgrade will bring to your SR income equivalent.
        otherwise as in findbest()
    
    Returns:
        int: The first amount of TC at which the upgrade is not worse anymore than using the TC otherwise.
    '''
    credits=upgradecost
    opc = opportunitycost(upgradecost,credits,enemytier,basestatbonus,cr,dr,sb)
    while opc>upgrademult:
        credits += 1
        opc = opportunitycost(upgradecost,credits,enemytier,basestatbonus,cr,dr,sb)
    return credits

def breakevenspeed(speednumber, wpm_now, wpm_next, enemytier,basestatbonus,cr,dr,sb):
    '''
    A specific version of findbreakeven() for the speed upgrades.
    
    Args:
        speednumber (int): Either 8 or 16
        wpm_now (number): Waves per min at your current highest speed, as found in the Round Statistics panel (based on default speed)
        wpm_next (number): Waves per min you estimate to get at the new speed. Should be between half and the full amount of your wpm_now.
        otherwise as in findbest()
    '''
    if speednumber not in (8,16):
        raise ValueError("Invalid input! First arg must either be 8 or 16.")
    upmult=(wpm_next / wpm_now * 2)**(1+enemytier)
    upcost=(10**3,10**5)[speednumber==16]
    return findbreakeven(upcost,upmult,enemytier,basestatbonus,cr,dr,sb)

#main execution
print("Welcome to the TPT Town Upgrades Optimizer by MarioVX!")
enemytier = int(input("\nIs the Enemy Tier you can farm still restricted by your Blueprint Tier and New Bounds, or is your BPT past that?\n"
    +"0 if you still use New Bounds to keep ET at/shortly below your BPT.\n1 if your BPT exceeds ET even at 0% NB.\n"))
if enemytier not in (0,1):
    raise ValueError("This must either be 0 or 1!")
basestatbonus = int(input("\nTo what base Statistics bonus do you plan to get up to in your upcoming TT, in percent without the %-sign?\n"
    +"If you want to check your current stat bonus for this but already have levels in the bonus stat goals town upgrade,\nremember to "
    +"divide it out first. E.g. if you have 25%, divide the displayed amount by 1.25.\nMax value is 640 if you did everything, 620 without any mission.\n"
    +"In general, from 640 subtract 10 for each uncompleted category and another 2 for each missing point.\n"))
if basestatbonus > 640 or basestatbonus < 20:
    raise ValueError("This should be at least 20 since you need to defeat the Cuboses to tier up, and at most 640.")
cr = int(input("\nWhat's your current level in TC per BPT conversion rate upgrade? From 0 to 10. You can tell by the cost:\n"
    +"Displayed Cost - Current level\n5 - 0\n8 - 1\n13 - 2\n22 - 3\n37 - 4\n61 - 5\n100 - 6\n166 - 7\n274 - 8\n453 - 9\nCompleted! - 10\n"))
if cr > costparameters["cr"][2] or cr < 0:
    raise ValueError("This must be from 0 to "+str(costparameters["cr"][2])+".")
dr = int(input("What's your current level in droprate increase per remaining Credit?\nRead this off the effect when *not* hovering over it, e.g. 1.3% is 13.\n"))
if dr > costparameters["dr"][2] or dr < 0:
    raise ValueError("This must be from 0 to "+str(costparameters["dr"][2])+".")
sb = int(input("What's your current level in bonus for statistic goals increase?\nGet this from the current effect by multiplying with 0.08, e.g. 37.5% is 3.\n"))
if sb > costparameters["sb"][2] or sb < 0:
    raise ValueError("This must be from 0 to "+str(costparameters["sb"][2])+".")
print("\nAlright, configuration complete!")
exit = False
while not exit:
    oper = input("\nWhat would you like to do?\n fb - Find the best allocation of TC across CR,DR,SB at the beginning of a TT (CR nevertheless spent at the end).\n "
        #+"la - Generate a list of all optimal allocations for your configuration across all amounts of TC\n "
        +"opc - Determine the opportunity cost (multiplier you're missing out on) of an upgrade at your point of progress.\n "
        +"fbe - Find the TC amount at which some upgrade you specify with estimated benefit breaks even.\n "
        +"bes - Find the TC amount at which a Speed upgrade in particular breaks even.\n")
    if oper not in ("fb","opc","fbe","bes"):
        raise ValueError("Unknown operation.")
    elif oper=="fb":
        credits = int(input("\nHow many TC are ready to be spent?\n"))
        res = findbest(credits,enemytier,basestatbonus,cr,dr,sb)
        print("\nGet up to levels "+str(res[0])+" in (CR,DR,SB) respectively.\n"
            +"Buy DR & SB right now, CR right before your next reset.\nThis gets you up to "+str(res[1])+" times the SR income without those TUs.")
    elif oper=="opc":
        credits = int(input("\nHow many TC are ready to be spent?\n"))
        upcost = int(input("\nHow many TC does the upgrade you're interested in cost?\n"))
        res = opportunitycost(upcost,credits,enemytier,basestatbonus,cr,dr,sb)
        print("\nIf you spent those credits normally rather than on the upgrade, you'd get "+str(res)+" times as much SR income equivalent.\n"
            +"Only buy it if you expect it to be better than this!")
    elif oper=="fbe":
        upcost = int(input("\nHow many TC does the upgrade you're interested in cost?\n"))
        upmult = float(input("\nWhat multiplier to your SR income equivalent do you expect to get out of it?\n"))
        res = findbreakeven(upcost,upmult,enemytier,basestatbonus,cr,dr,sb)
        print("\nUnder your assumptions, the upgrade in question would break even at "+str(res)+" TC to spend.")
    elif oper=="bes":
        speednum = int(input("\nWhich speed upgrade are we talking about - 8 or 16?\n"))
        wpm_now = float(input("\nWhat's the Waves per minute at your current highest speed, as found in Round Statistics panel (based on default speed)?"))
        wpm_next = float(input("\nHow much WPM do you expect to get at that upcoming speed? Should be somewhere between half and the full amount of your current."))
        res = breakevenspeed(speednum,wpm_now,wpm_next,enemytier,basestatbonus,cr,dr,sb)
        print("\nWith those WPM values, the speed upgrade should break even at "+str(res)+" TC to spend.")
    exit = bool(int(input("\nDo you want to exit? 1 for yes, 0 for no. If not, another calculation can be run.")))