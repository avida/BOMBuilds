#!/usr/bin/python
#coding=utf8
import sys
import uuid
import re
time_exp = re.compile('^\d{1,2}:\d{1,2}$')
supply_exp = re.compile('^\d{1,2}$')
ColloquialToCodeDictionary = {
   'SupplyDepot'   : ['supply', 'Supply'],
   'Barracks'      : ['Barracks'],
   'Bunker'        : ['Bunker'],
   'Refinery'      : ['refinery','Refinery'],
   'EngineeringBay': ['Engineering Bay'],
   'CommandCenter' : ['command', 'Command Center'],
   'Factory'       : ['Factory'],
   'Starport'      : ['cosmoport','Starport'],
   'Armory'       : ['Armory'],
   'SCV'           : ['SCV'],
   'Marine'        : ['Marine'],
   'Marauder'      : ['Marauder'],
   'Medivac'           : ['Medivac'],
   'Hellion'           : ['Hellion'],
   'HellionTank'       : ['Hellbat'],
   'Reaper'            : ['Reaper'],
   'BarracksReactor'   : ['BarracksReactor','reactor_barrack'],
   'FactoryReactor'    : ['FactoryReactor', 'reactor_fact'],
   'StarportReactor'   : ['StarportReactor'],
   'FactoryTechLab'    : ['FactoryTechLab', 'lab_fact'],
   'BarracksTechLab'    : ['BarracksTechLab', 'lab_barrack'],
   'StarportTechLab'    : ['StarportTechLab'],
}

AbilityCodeDictionary = {
   '"UpgradeToOrbital", 0'       : ['Orbital' ],
   '"EngineeringBayResearch", 2' : ['+1_terran_infantry_attack', '+1 Infantry Attack'],
   '"EngineeringBayResearch", 6' : ['+1 Infantry Armor'],
   '"ArmoryResearch", 5' : ['+1 Vehicle Weapon', '+1 Vehicle weapon'],
   '"BarracksTechLabResearch", 0': ['Stimpack'],
   '"BarracksTechLabResearch", 1': ['Combat Shield', 'Combat shields'],
   '"BarracksTechLabResearch", 2': ['Fugas', 'Concussive shells'],
}

def ColloqiualToCode(name):
   for key in ColloquialToCodeDictionary.keys():
      if (name in ColloquialToCodeDictionary[key]):
         return key
   raise Exception('Unknown name ' + name);

def GetAbilityCode(name):
   for key in AbilityCodeDictionary.keys():
      if (name in AbilityCodeDictionary[key]):
         return key
   raise Exception('Unknown ability ' + name);

def isAbility(name):
   if name[:1] == '+':
      return True
   for key in AbilityCodeDictionary.keys():
      if (name in AbilityCodeDictionary[key]):
         return True
   return False
try:
   filename = sys.argv[1]
except Exception:
   print 'specify correct file name in cmd line'
   sys.exit(0)
f = open(filename,'r')
outfile = '.'.join(filename.split('.')[:1]+['bo'])
out = open(outfile, 'w')
counter = 0
infoCounter = 0
for s in f:
   if 'Objectives:' in s:
      break;
   line =  s.strip().split()
   if len(line) == 0:
      continue
   if(s[:1] == '#'):
      continue
   if(s[:1] == 'I'):
      #read Info tip
      time = line[1]
      try:
         minutes = int(time.split(':')[0])
         seconds = int(time.split(':')[1])
      except ValueError:
         print "error parsing line\n %s" % " ".join(line)
         break
      info = " ".join(line[2:])
      out.write('gv_bOInfoTips[%d] = "%s";\n' % (infoCounter, info) )
      out.write('gv_bOInfoTimings[%d] = %d;\n' % (infoCounter, minutes* 60 + seconds) )
      infoCounter += 1
   else:
      time = line[0]
      minutes = int(time.split(':')[0])
      seconds = int(time.split(':')[1])
      try:
         supply = line[1]
         if not supply_exp.match(supply):
            supply = 0
            name = " ".join(line[1:])
         else:
            supply = int(line[1])
            name = " ".join(line[2:])
      except ValueError:
         print "error parsing line\n %s" % " ".join(line)
         break
      if not isAbility(name):
         name = ColloqiualToCode(name)
         out.write("gv_bOUnits[%d] = \"%s\";\n" % (counter, name))
      else:
         ability_code = GetAbilityCode(name)
         out.write("gv_bOAbilities[%d] = AbilityCommand(%s);\n" % (counter, ability_code))
         out.write("gv_bOAbilities_Name[%d] = gf_GetAbilityName(AbilityCommand(%s));\n" % (counter, ability_code))
      out.write("gv_bOSupplies[%d] = %d;\n" % (counter, supply))
      out.write("gv_bOTimings[%d][0] = %d;\n" % (counter, minutes))
      out.write("gv_bOTimings[%d][1] = %d;\n" % (counter, seconds))
      counter +=1
out.write('gv_bOEnd = %d;\n'% counter)
counter =0
# Writing objectives
for s in f:
   try:
      line =  s.strip().split()
      if len(line) == 0:
         continue
      time = line[0]
      try:
         supply = int(line[1])
         name = " ".join(line[2:])
         minutes = int(time.split(':')[0])
         seconds = int(time.split(':')[1])
      except ValueError:
         print "error parsing line\n %s" % " ".join(line)
         break
   except IndexError:
      print "error in line " + s
   out.write("gv_bOObjectivesUnits[%d] = \"%s\";\n" % (counter, ColloqiualToCode(name)))
   out.write("gv_bOObjectivesUnitsAmount[%d] = %d;\n" % (counter, supply))
   out.write("gv_bOObjectivesTimings[%d] = %d;\n" % (counter, minutes*60 + seconds))
   counter += 1
out.write("gv_bOObjectivesCount = %d;\n" % (counter))
#out.write('gv_bOuuid="%s"' % uuid.uuid4())
out.close()
print 'Converting done'
print 'out file is '+ outfile
