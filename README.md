# pynigma

An Enigma machine simulator written in Python.  Supports 3-wheel, 4-wheel and railway (K-type) Enigma machines with support for specifying rotors, reflectors and plugboards.

## Decoding

pynigma.py --help shows the options.  There are a ton of them, so here's an example of how to configure the system to decode Turing's sample message to the recruits at Bletchley Park (http://wiki.franklinheath.co.uk/index.php/Enigma/Sample_Messages#Turing.27s_Treatise.2C_1940)

```bash
$ cat turing.message | ./pynigma.py --reflector railway --reflector_ring 26 --reflector_position J --rotors III-K,I-K,II-K --rings 17,16,13 --positions E,Z,A --ETW railway
```

Which produces the output:
```text
DEUTS QETRU PPENS INDJE TZTIN ENGLA ND
```
Mirroring the fact that the input is broken into groups of five characters.

Cleaning up a bit and following a handful of conventions (eg: Q=>CH) you get:
```text
DEUTSCHE TRUPPEN SIND JETZT IN ENGLAND
```
Keep in mind that due to the historical uses of the Enigma machine, a lot of the sample inputs are in German.  Translating gives:
```text
German troops are now in England
```
Suggesting, I think, that Turing wanted to keep people focused on the task at hand.

You can include the --trace option if you want to see the path each letter takes through the system:

```text
  in   plugs   ETW    II-K   I-K   III-K  rail-K III-K   I-K    II-K   ETW   plugs   out  rotors 
  Q     Q=>Q  Q=>00  00=>19 19=>06 06=>25 25=>05 05=>18 18=>24 24=>11 11=>D   D=>D    D     EZB  
  S     S=>S  S=>10  10=>23 23=>08 08=>24 24=>11 11=>00 00=>10 10=>02 02=>E   E=>E    E     EZC  
  Z     Z=>Z  Z=>05  05=>06 06=>05 05=>09 09=>02 02=>25 25=>16 16=>06 06=>U   U=>U    U     EZD  
  V     V=>V  V=>21  21=>17 17=>22 22=>12 12=>08 08=>09 09=>05 05=>04 04=>T   T=>T    T     EZE  
```

## Encoding
The Enigma machine is symmetric: encoding is the same as decoding:

```bash
$ echo HELLO WORLD | ./pynigma.py
ILBDA AMTAZ
```

```bash
$ echo ILBDA AMTAZ | ./pynigma.py
HELLO WORLD
```

Here we're using the default settings: Rotors I, II, III, reflector B and everything in position A with no plugs in the plugboard.
