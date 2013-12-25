#!/usr/bin/python

# pynigma.py
#
# Andrew Logan - 12/21/2013
#
# Enigma simulator written in python

import sys
import argparse
import ConfigParser

#Ja, ist plugboard!
class Steckerbrett:
    letters = None

    def __init__(self, steckerbrett_filename):
        #Set up our memory
        self.letters = []

        config = ConfigParser.ConfigParser()
        config.read(steckerbrett_filename)
        
        #And now load the letter map
        for x in range(0, 26, 1):
            current_letter = chr(x+ord("A"))
            target_letter = config.get("wiring", current_letter)
            self.letters.append(target_letter)

    def encode(self, input_letter):
        return self.letters[ord(input_letter) - ord('A')]

class EnigmaETW:
    name = None
    letters = None

    def __init__(self, etw_filename):
        self.letters = []

        #We have the filename from the part of the code that called us
        config = ConfigParser.ConfigParser()
        config.read(etw_filename)

        #Load the letter map
        for x in range(0, 26, 1):
            current_letter = chr(x+ord("A"))
            target_letter = config.get("wiring", current_letter)
            self.letters.append(target_letter)

    #The idea is that I want to start from a pin, find the letter that maps to and then find which pin that is.
    def encode(self, input_letter):
        index = ord(input_letter) - ord('A')

        output_letter = self.letters[index]

        #The reflector doesn't rotate, so this isn't so bad.
        output_pin = ord(output_letter) - ord('A')

        return output_pin

    #And reverse that operation
    def backwards_encode(self, input_pin):
        #The reverse encoding is a little weird because of the data structure I'm using.  To decode 02, for example, I need to convert it back into a letter ("C"), and then scan through the character map until I find it.  The position where the character appears is the letter it should be converted back into.

        input_letter = chr(input_pin + ord('A'))

        for x in range(0, len(self.letters)):
            if(self.letters[x] == input_letter):
                output_letter = chr(x + ord('A'))
                return output_letter

        #Uh...
        print "Failed to decode letter in ETW"
        return 'A'

class EnigmaReflector:
    name = None
    letters = None
    orientation = None
    indicator = None

    def __init__(self, reflector_filename, reflector_position, reflector_offset):
        self.letters = []

        #The outer ring can move around the inner wires
        reflector_offset = ord(reflector_offset) - ord('A')

        #The files I'm using to load this system all start from 'A'
        self.indicator = chr(ord('A') + reflector_offset)
        self.orientation = 0

        #We have the filename from the part of the code that called us
        config = ConfigParser.ConfigParser()
        config.read(reflector_filename)

        #Read the rotor configuration file
        self.name = config.get("reflector", "name")

        #And now load the letter map
        for x in range(0, 26, 1):
            current_letter = chr(x+ord("A"))
            target_letter = config.get("wiring", current_letter)
            self.letters.append(target_letter)

        #And rotate to the appropriate position
        while(self.indicator != reflector_position):
            self.advance()

    def advance(self):
        new_letters = self.letters[1:]
        new_letters.append(self.letters[0])

        self.letters = new_letters
        
        new_orientation = (self.orientation + 1) % 26
        self.orientation = new_orientation

        new_indicator = ((ord(self.indicator)-ord('A'))+1) % 26
        self.indicator = chr(new_indicator + ord('A'))

    #Return the letter that would be showing through the window
    def get_indicator(self):
        return self.indicator

    #The idea is that I want to start from a pin, find the letter that maps to and then find which pin that is.

    def encode(self, input_pin):
        output_letter = self.letters[input_pin]
        
        #What position is this rotor in?
        # rotor_offset = (ord(self.indicator) - ord('A'))

        #Apply the offset
        output_pin = ((ord(output_letter) - ord('A')) - self.orientation) % 26

        return output_pin

class EnigmaRotor:
    name = None
    notches = None
    letters = None
    immobile = None
    indicator = None
    orientation = None

    def __init__(self, rotor_filename, target_indicator, ring_position):
        #Set up our memory
        self.notches = []
        self.letters = []
        self.immobile = False

        #The outer ring can move around the inner wires
        ring_offset = ord(ring_position) - ord('A')

        #The files I'm using to load this system all start from 'A'
        self.indicator = chr(ord('A') + ring_offset)  
        self.orientation = 0

        #We have the filename from the part of the code that called us
        config = ConfigParser.ConfigParser()
        config.read(rotor_filename)

        #Read the rotor configuration file
        self.name = config.get("rotor", "name")

        self.notches.append(config.get("rotor", "notch_1"))
        self.notches.append(config.get("rotor", "notch_2"))
        
        #And now load the letter map.
        self.letter_map = {}

        for x in range(0, 26, 1):
            current_letter = chr(x+ord("A"))
            target_letter = config.get("wiring", current_letter)
            self.letter_map[current_letter] = target_letter

        #Build the forward mapping:
        for x in range(0, 26, 1):
            current_letter = chr(x+ord("A"))
            self.letters.append(self.letter_map[current_letter])

        #And rotate the letter map until we get to the right position
        while(self.indicator != target_indicator):
            self.advance()

    def set_immobile(self, immobile):
        self.immobile = immobile

    #The idea is that we want to find the letter that the pin maps to, and then find which pin that letter maps to.
    def encode(self, input_pin):
        output_letter = self.letters[input_pin]
        
        #What position is this rotor in?
        # rotor_offset = (ord(self.indicator) - ord('A'))

        #Apply the offset
        output_pin = ((ord(output_letter) - ord('A')) - self.orientation) % 26

        return output_pin

    #For encoding when the signal is coming from the left (from the reflector back to the lightboard)
    def backwards_encode(self, input_pin):
        #What position is this rotor in?
        # rotor_offset = (ord(self.indicator) - ord('A'))

        #So figure out which letter this is
        input_letter = chr(((input_pin + self.orientation) % 26) + ord('A'))

        for x in range(0, 26):
            if(self.letters[x] == input_letter):
                return x

    def advance(self):
        if(self.immobile):
            return

        new_letters = self.letters[1:]
        new_letters.append(self.letters[0])

        self.letters = new_letters
        
        new_orientation = (self.orientation + 1) % 26
        self.orientation = new_orientation

        new_indicator = ((ord(self.indicator)-ord('A'))+1) % 26
        self.indicator = chr(new_indicator + ord('A'))

    #Return the letter that would be showing through the window
    def get_indicator(self):
        return self.indicator

class EnigmaMachine:
    """Class that aims to replicate the behavior of the three and four-rotor Enigma machines.  Note that the fourth rotor doesn't index like the other three, so a 4-rotor machine can be made to act like a three-rotor machine by skipping the fourth rotor."""

    rotors = None
    etw = None
    reflector = None
    steckerbrett = None
    trace_format_string = None

    def get_pin_from_letter(self, letter):
        return self.etw.encode(letter)

    def get_letter_from_pin(self, pin):
        return self.etw.backwards_encode(pin)

    def get_letters(self, item):
        letter_str = ""

        for x in range(0, 26, 1):
            letter_str += item.letters[x] + ","

        return letter_str

    def make_rotor_filename(self, rotor_name):
        return rotor_name + ".rotor"

    def make_etw_filename(self, rotor_name):
        return rotor_name + ".ETW"

    def make_reflector_filename(self, reflector_name):
        return reflector_name + ".reflector"

    def make_steckerbrett_filename(self, steckerbrett_name):
        return steckerbrett_name + ".steckerbrett"

    def print_config(self):
        for rotor in self.rotors:
            print "Rotor " + rotor.name + " has map: " + self.get_letters(rotor) + "inverted: " + self.get_back_letters(rotor) + " and notches: " + str(rotor.notches)

        print "Reflector " + self.reflector.name + " has map: " + self.get_letters(self.reflector)

        print "Steckerbrett has map: " + self.get_letters(self.steckerbrett)

    def print_trace_header(self):
        print self.trace_format_string.format(*self.trace_header_strings)

    def print_state(self, input, output):
        print self.format_string.format(input, output, self.reflector.name, self.rotors[2].get_indicator(), self.rotors[1].get_indicator(), self.rotors[0].get_indicator())

    def trace_setup(self):
        format_token_number = 0

        #input char
        self.trace_format_string += "{"+str(format_token_number)+":^6} "
        self.trace_header_strings.append("in")

        #stecker
        format_token_number += 1
        self.trace_format_string += "{"+str(format_token_number)+":^6} "
        self.trace_header_strings.append("plugs")

        #First pass through the entrywheel
        format_token_number += 1
        self.trace_format_string += "{"+str(format_token_number)+":^6} "
        self.trace_header_strings.append("ETW")

        #First pass through the rotors
        for rotor in self.rotors:
            format_token_number += 1
            self.trace_format_string += "{"+str(format_token_number)+":^6} "
            self.trace_header_strings.append(rotor.name)

        #Reflector
        format_token_number += 1
        self.trace_format_string += "{"+str(format_token_number)+":^6} "
        self.trace_header_strings.append(self.reflector.name)

        #Second pass through the rotors
        for rotor in reversed(self.rotors):
            format_token_number += 1
            self.trace_format_string += "{"+str(format_token_number)+":^6} "
            self.trace_header_strings.append(rotor.name)

        #Entrywheel again
        format_token_number += 1
        self.trace_format_string += "{"+str(format_token_number)+":^6} "
        self.trace_header_strings.append("ETW")

        #stecker again
        format_token_number += 1
        self.trace_format_string += "{"+str(format_token_number)+":^6} "
        self.trace_header_strings.append("plugs")

        #output
        format_token_number += 1
        self.trace_format_string += "{"+str(format_token_number)+":^6}"
        self.trace_header_strings.append("out")

        #and the state of the rotors
        format_token_number += 1
        self.trace_format_string += "{"+str(format_token_number)+":^7}"
        self.trace_header_strings.append("rotors")

    def __init__(self, rotor_names, rotor_positions, ring_positions, etw_name, reflector_name, reflector_position, reflector_ring, steckerbrett_name):
        #set up our memory
        self.rotors = []
        
        self.trace_format_string = ""
        self.trace_header_strings = []

        #Load the wheels from right to left (eg: wheel 0 is the rightmost one)
        rotor_count = 1
        for rotor_name in rotor_names:
            current_rotor = rotor_count-1
            self.rotors.append(EnigmaRotor(self.make_rotor_filename(rotor_name), rotor_positions[current_rotor], ring_positions[current_rotor]))
            rotor_count += 1

        #And flip the rotors around so that the fast rotor is the rightmost one
        self.rotors.reverse()
        
        #How many rotors did we just define?
        if(len(self.rotors) > 3):
            rotors[len(self.rotors)-1].set_immobile(True)

        #We only have one entry wheel
        self.etw = EnigmaETW(self.make_etw_filename(etw_name))

        #one reflector
        self.reflector = EnigmaReflector(self.make_reflector_filename(reflector_name), reflector_position, reflector_ring)
        
        #And, of course, only one plugboard
        self.steckerbrett = Steckerbrett(self.make_steckerbrett_filename(steckerbrett_name))

        self.trace_setup()

    def advance_rotors(self):
        #Figure out the current state of the system
        rotors_to_advance = {}

        rotors_to_advance[0] = True

        current_rotor = -1
        for rotor in self.rotors:
            current_rotor += 1
            current_indicator = rotor.get_indicator()
            
            for notch in rotor.notches:
                if(current_indicator == notch):
                    rotors_to_advance[current_rotor] = True
                    rotors_to_advance[current_rotor+1] = True
                    break;

        #And push forward the rotors
        for rotor_number in rotors_to_advance:
            if(rotor_number < len(self.rotors)):
                self.rotors[rotor_number].advance()

    #Encoding a letter involves advancing rotors and then tracing the path of the input signal through the appropriate steckers and rotors and such
    def encode(self, input_letter, do_trace):
        self.advance_rotors()

        trace_output = []

        trace_output.append(input_letter)

        #First through the plugboard
        stecker_output = self.steckerbrett.encode(input_letter)
        trace_output.append(input_letter + "=>" + stecker_output)

        #Then figure out which pin is energized
        intermediate_pin = self.get_pin_from_letter(stecker_output)
        trace_output.append(stecker_output + "=>" + "{0:02}".format(intermediate_pin))

        # trace_output.append(intermediate_pin)

        # print "pins:",
        # print str(intermediate_pin) + " =>",
        
        #Then through the rotors
        for rotor in self.rotors:
            new_intermediate_pin = rotor.encode(intermediate_pin)
            trace_output.append("{0:02}".format(intermediate_pin) + "=>" + "{0:02}".format(new_intermediate_pin))

            intermediate_pin = new_intermediate_pin

        #Reflector!
        new_intermediate_pin = self.reflector.encode(intermediate_pin)
        trace_output.append("{0:02}".format(intermediate_pin) + "=>" + "{0:02}".format(new_intermediate_pin))
        intermediate_pin = new_intermediate_pin

        #trace_output.append(intermediate_pin)
        # print str(intermediate_pin) + " =>",

        output_pin = None
        #And through the rotors the other way
        for rotor in reversed(self.rotors):
            new_intermediate_pin = rotor.backwards_encode(intermediate_pin)
            trace_output.append("{0:02}".format(intermediate_pin) + "=>" + "{0:02}".format(new_intermediate_pin))

            intermediate_pin = new_intermediate_pin
            output_pin = intermediate_pin

        #Convert the pin back to a letter
        output_letter = self.get_letter_from_pin(output_pin)
        trace_output.append("{0:02}".format(intermediate_pin) + "=>" + output_letter)

        #Back through the stecker
        final_letter = self.steckerbrett.encode(output_letter)
        trace_output.append(output_letter + "=>" + final_letter)

        trace_output.append(final_letter)

        #Get the state of the indicators
        indicators = ""
        for rotor in self.rotors:
            indicators = rotor.indicator + indicators

        trace_output.append(indicators)

        # print final_letter

        if(do_trace):
            print self.trace_format_string.format(*trace_output)

        return final_letter

def main(argv=None):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--rotors", help="Ordered, comma-separated list of rotors to use.", default="I,II,III")
    parser.add_argument("--rings", help="Ordered, comma-separated list of ring settings to use.  Either letters or numbers are fine.", default="A,A,A")
    parser.add_argument("--positions", help="Ordered, comma-separated list of initial positions to use.  Either letters or numbers are fine.", default="A,A,A")
    parser.add_argument("--reflector", help="Which reflector to use", default="B", choices=["A", "B", "C", "B_thin", "C_thin", "railway"])
    parser.add_argument("--reflector_position", help="What position to set the reflector to.", default="A")
    parser.add_argument("--reflector_ring", help="Ring setting for use on the reflector wheel.", default="A")
    parser.add_argument("--steckerbrett", help="Which plugboard settings to use", default="default") 
    parser.add_argument("--ETW", help="The wiring of the entry wheel.", default="default") 
    parser.add_argument("--trace", help="Trace the electrical path through the machine.", action="store_true") 
    parser.add_argument("--extract_key", help="Extract the message key from the beginning of the encoded message.", action="store_true") 

    args = parser.parse_args()

    rotor_names = args.rotors.split(",")
    
    rotor_positions = args.positions.split(",")
    
    #Convert numbers to letters
    for x in range(0, len(rotor_positions)):
        if rotor_positions[x].isdigit():
            rotor_position_int = int(rotor_positions[x])
            rotor_positions[x] = chr(ord('A') + rotor_position_int - 1)

    ring_positions = args.rings.split(",")

    #Convert numbers to letters
    for x in range(0, len(ring_positions)):
        if ring_positions[x].isdigit():
            ring_position_int = int(ring_positions[x])
            ring_positions[x] = chr(ord('A') + ring_position_int - 1)

    reflector_name = args.reflector
    
    reflector_position = args.reflector_position

    reflector_ring = args.reflector_ring

    #Convert numbers to letters
    if reflector_ring.isdigit():
        reflector_ring_int = int(reflector_ring)
        reflector_ring = chr(ord('A') + reflector_ring_int - 1)
    
    steckerbrett_name = args.steckerbrett

    etw_name = args.ETW

    machine = EnigmaMachine(rotor_names, rotor_positions, ring_positions, etw_name, reflector_name, reflector_position, reflector_ring, steckerbrett_name)

    trace = args.trace

    extract_key = args.extract_key

    if(trace):
        machine.print_trace_header()

    output_array = []

    for char in sys.stdin.read().upper():
        if(ord(char) >= ord('A') and ord(char) <= ord('Z')):
            #Run it through the machine if it's a letter
            char = machine.encode(char, trace)
            output_array.append(char)

        #Preserve the formatting of the original message if this isn't trace mode
        if(not trace):
            sys.stdout.write(char)

        if(extract_key and (len(output_array) == 6)):
            for x in range(0,3):
                #We know that the german enigma operators would start messages with two copies of the message key
                if(output_array[x] != output_array[3+x]):
                    print "Failed to match key!"
                    return

            #Set up a new machine with the new key
            print "\nExtracted new key: " + "".join(output_array[:3])
            machine = EnigmaMachine(rotor_names, output_array[:3], ring_positions, etw_name, reflector_name, reflector_position, reflector_ring, steckerbrett_name)

    #Toss a newline on the end
    print

#Give main() a single exit point (see: http://www.artima.com/weblogs/viewpost.jsp?thread=4829)
if __name__ == "__main__":
    sys.exit(main(sys.argv))
