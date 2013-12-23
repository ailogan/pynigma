#!/usr/bin/python

# pynigma.py
#
# Andrew Logan - 12/21/2013
#
# Enigma simulator written in python

import sys
import argparse
import ConfigParser

class EnigmaReflector:
    name = None
    letter_map = None

    def __init__(self, reflector_filename):
        self.letter_map = {}

        #We have the filename from the part of the code that called us
        config = ConfigParser.ConfigParser()
        config.read(reflector_filename)

        #Read the rotor configuration file
        self.name = config.get("reflector", "name")

        #And now load the letter map
        for x in range(0, 26, 1):
            current_letter = chr(x+ord("A"))
            target_letter = config.get("wiring", current_letter)
            self.letter_map[current_letter] = target_letter
        

class EnigmaRotor:
    name = None
    notches = None
    letter_map = None

    def __init__(self, rotor_filename):
        #Set up our memory
        self.notches = []
        self.letter_map = {}

        #We have the filename from the part of the code that called us
        config = ConfigParser.ConfigParser()
        config.read(rotor_filename)

        #Read the rotor configuration file
        self.name = config.get("rotor", "name")

        self.notches.append(config.get("rotor", "notch_1"))
        self.notches.append(config.get("rotor", "notch_2"))
        
        #And now load the letter map
        for x in range(0, 26, 1):
            current_letter = chr(x+ord("A"))
            target_letter = config.get("wiring", current_letter)
            self.letter_map[current_letter] = target_letter

class EnigmaMachine:
    """Class that aims to replicate the behavior of the three and four-rotor Enigma machines.  Note that the fourth rotor doesn't index like the other three, so a 4-rotor machine can be made to act like a three-rotor machine by skipping the fourth rotor."""

    rotors = None
    reflector = None
    
    def make_rotor_filename(self, rotor_name):
        return rotor_name + ".rotor"

    def make_reflector_filename(self, reflector_name):
        return reflector_name + ".reflector"

    def __init__(self, rotor_names, reflector_name):
        
        #set up our memory
        self.rotors = []

        #Load the wheels from right to left (eg: wheel 0 is the rightmost one)
        for rotor_name in rotor_names:
            self.rotors.append(EnigmaRotor(self.make_rotor_filename(rotor_name)))

        #We can only have one reflector
        self.reflector = EnigmaReflector(self.make_reflector_filename(reflector_name))

        for rotor in self.rotors:
            letter_map = rotor.letter_map
            letter_str = ""

            for x in range(0, 26, 1):
                current_letter = chr(x+ord("A"))
                letter_str += letter_map[current_letter] + ","
            
            print "Rotor " + rotor.name + " has map: " + letter_str + " and notches: " + str(rotor.notches)

        reflector_letter_map = self.reflector.letter_map
        reflector_letter_str = ""

        for x in range(0, 26, 1):
            current_letter = chr(x+ord("A"))
            reflector_letter_str += reflector_letter_map[current_letter] + ","

        print "Reflector " + self.reflector.name + " has map: " + reflector_letter_str
            

def main(argv=None):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--rotors", help="Ordered, comma-separated list of rotors to use.", default="I,II,III")
    parser.add_argument("--reflector", help="Which reflector to use", default="B", choices=["B", "C", "B_thin", "C_thin"])
    
    args = parser.parse_args()

    rotor_names = args.rotors.split(",")
    
    reflector_name = args.reflector

    machine = EnigmaMachine(rotor_names, reflector_name)
    


#Give main() a single exit point (see: http://www.artima.com/weblogs/viewpost.jsp?thread=4829)
if __name__ == "__main__":
    sys.exit(main(sys.argv))
