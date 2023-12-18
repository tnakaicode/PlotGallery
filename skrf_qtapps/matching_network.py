import math
import os

def PrintScheme(top, LC):
	match top:
		case 1:
			match LC:
				case 1:
					print('  o────┬── C1 ──┐');
					print('       │        │');
					print('       │        │');
					print('Z0     L2       ZL');
					print('       │        │');
					print('       │        │');
					print('  o────┴────────┘');
					print('\n---------------------');
				case 2:
					print('  o────┬── L1 ──┐');
					print('       │        │');
					print('       │        │');
					print('Z0     C2       ZL');
					print('       │        │');
					print('       │        │');
					print('  o────┴────────┘');
					print('\n---------------------');
				case 3:
					print('  o────┬── L1 ──┐');
					print('       │        │');
					print('       │        │');
					print('Z0     L2       ZL');
					print('       │        │');
					print('       │        │');
					print('  o────┴────────┘');
					print('\n---------------------');
				case 4:
					print('  o────┬── C1 ──┐');
					print('       │        │');
					print('       │        │');
					print('Z0     C2       ZL');
					print('       │        │');
					print('       │        │');
					print('  o────┴────────┘');
					print('\n---------------------');
		case 2:
			match LC:
				case 1:
					print('  o─── L2 ──┬───┐');
					print('            │   │');
					print('            │   │');
					print('Z0          C1  ZL');
					print('            │   │');
					print('            │   │');
					print('  o─────────┴───┘');
					print('\n---------------------');
				case 2:
					print('  o─── C2 ──┬───┐');
					print('            │   │');
					print('            │   │');
					print('Z0          L1  ZL');
					print('            │   │');
					print('            │   │');
					print('  o─────────┴───┘');
					print('\n---------------------');
				case 3:
					print('  o─── L2 ──┬───┐');
					print('            │   │');
					print('            │   │');
					print('Z0          L1  ZL');
					print('            │   │');
					print('            │   │');
					print('  o─────────┴───┘');
					print('\n---------------------');
				case 4:
					print('  o──── C2 ─┬───┐');
					print('            │   │');
					print('            │   │');
					print('Z0          C1  ZL');
					print('            │   │');
					print('            │   │');
					print('  o─────────┴───┘');
					print('\n---------------------');
		case 3:
			match LC:
				case 1:
					print('  o─── L2 ──┬───┐');
					print('            │   │');
					print('            │   │');
					print('Z0          C1  ZL');
					print('            │   │');
					print('            │   │');
					print('  o─────────┴───┘');
					print('\n---------------------');
				case 2:
					print('  o─── C2 ──┬───┐');
					print('            │   │');
					print('            │   │');
					print('Z0          L1  ZL');
					print('            │   │');
					print('            │   │');
					print('  o─────────┴───┘');
					print('\n---------------------');
				case 3:
					print('  o───── C1 ────┐');
					print('                │');
					print('                │');
					print('Z0              ZL');
					print('                │');
					print('                │');
					print('  o─────────────┘');
					print('\n---------------------');
				case 4:
					print('  o───── L1 ────┐');
					print('                │');
					print('                │');
					print('Z0              ZL');
					print('                │');
					print('                │');
					print('  o─────────────┘');
					print('\n---------------------');
		case 4:
			match LC:
				case 1:
					print('  o────┬── C1 ──┐');
					print('       │        │');
					print('       │        │');
					print('Z0     L2       ZL');
					print('       │        │');
					print('       │        │');
					print('  o────┴────────┘');
					print('\n---------------------');
				case 2:
					print('  o────┬── L1 ──┐');
					print('       │        │');
					print('       │        │');
					print('Z0     C2       ZL');
					print('       │        │');
					print('       │        │');
					print('  o────┴────────┘');
					print('\n---------------------');
				case 3:
					print('  o───────┬─────┐');
					print('          │     │');
					print('          │     │');
					print('Z0        C1    ZL');
					print('          │     │');
					print('          │     │');
					print('  o───────┴─────┘');
					print('\n---------------------');
				case 4:
					print('  o───────┬─────┐');
					print('          │     │');
					print('          │     │');
					print('Z0        L1    ZL');
					print('          │     │');
					print('          │     │');
					print('  o───────┴─────┘');
					print('\n---------------------');
	return;

def MatchingNetworkCalculation(X1, X2, B1, B2, f, top):
	w = float();																					# Angular frequency.
	L1 = float();																					# Matching network inductance and capacitance;
	L2 = float();
	C1 = float();
	C2 = float();
	LC = int();																						# Specific case identifier;
	w = 2.0 * math.pi * f;

	match top:
		case 1:
			if (X1 > 0):
				L1 = X1 / w;
				print('L1 = %11.5e H' % L1);
				if (X2 > 0):
					L2 = X2 / w;
					print('L2 = %11.5e H' % L2);
					LC = 3;
					PrintScheme(top, LC);
				if (X2 < 0):
					C2 = -1.0 / (w * X2);
					print('C2 = %11.5e F' % C2);
					LC = 2;
					PrintScheme(top, LC);
			if (X1 < 0):
				C1 = -1.0 / (w * X1);
				print('C1 = %11.5e F' % C1);
				if (X2 > 0):
					L2 = X2 / w;
					print('L2 = %11.5e H' % L2);
					LC = 1;
					PrintScheme(top, LC);
				if (X2 < 0):
					C2 = -1.0 / (w * X2);
					print('C2 = %11.5e F' % C2);
					LC = 4;
					PrintScheme(top, LC);
		case 2:
			if (B1 > 0):
				C1 = B1 / w;
				print('C1 = %11.5e F' % C1);
				if (B2 > 0):
					C2 = B2 / w;
					print('C2 = %11.5e F' % C2);
					LC = 4;
					PrintScheme(top, LC);
				if (B2 < 0):
					L2 = -1.0 / (w * B2);
					print('L2 = %11.5e H' % L2);
					LC = 1;
					PrintScheme(top, LC);
			if (B1 < 0):
				L1 = -1.0 / (w * B1);
				print('L1 = %11.5e H' % L1);
				if (B2 > 0):
					C2 = B2 / w;
					print('C2 = %11.5e F' % C2);
					LC = 2;
					PrintScheme(top, LC);
				if (B2 < 0):
					L2 = -1.0 / (w * B2);
					print('L2 = %11.5e H' % L2);
					LC = 3;
					PrintScheme(top, LC);
		case 3:
			if (X1 < 0):
				C1 = -1.0 / (w * X1);
				print('C1 = %11.5e F' % C1);
				LC = 3;
				PrintScheme(top, LC);
			if (X1 > 0):
				L1 = X1 / w;
				print('L1 = %11.5e H' % L1);
				LC = 4;
				PrintScheme(top, LC);
			if (B1 > 0):
				C1 = B1 / w;
				print('C1 = %11.5e F' % C1);
				L2 = -1.0 / (w * B2);
				print('L2 = %11.5e H' % L2);
				LC = 1;
				PrintScheme(top, LC);
			if (B1 < 0):
				L1 = -1.0 / (w * B1);
				print('L1 = %11.5e H' % L1);
				C2 = B2 / w;
				print('C2 = %11.5e F' % C2);
				LC = 2;
				PrintScheme(top, LC);
		case 4:
			if (B1 > 0):
				C1 = B1 / w;
				print('C1 = %11.5e F' % C1);
				LC = 3;
				PrintScheme(top, LC);
			if (B1 < 0):
				L1 = -1.0 / (w * B1);
				print('L1 = %11.5e H' % L1);
				LC = 4;
				PrintScheme(top, LC);
			if (X1 < 0):
				C1 = -1.0 / (w * X1);
				print('C1 = %11.5e F' % C1);
				L2 = X2 / w;
				print('L2 = %11.5e H' % L2);
				LC = 1;
				PrintScheme(top, LC);
			if (X1 > 0):
				L1 = X1 / w;
				print('L1 = %11.5e H' % L1);
				C2 = -1.0 / (w * X2);
				print('C2 = %11.5e F' % C2);
				LC = 2;
				PrintScheme(top, LC);
	return;

RL = float();																					# Load resistance and reactance;
XL = float();
GL = float();																					# Load conductance and susceptance;
BL = float();
f = float();																					# Operating frequency;
Z0 = float();																					# Nominal impedance and admittance;
Y0 = float();

top = int();																					# Topology identifier;
X1 = float();																					# Matching network reactance;
X2 = float();
B1 = float();																					# Matching network susceptance;
B2 = float();

ch = str(1);
zero = float(1e-12);

print('Symbols used in the program:');
print('Load resistance:        RL');
print('Load reactance:         XL');
print('Load complex impedance: ZL = RL + j*XL');
print('Nominal impedance:      Z0');
print('Operating frequency:    f\n');

while ch != 'z':
	X1 = X2 = B1 = B2 = 0.0;
	print('Enter input data.');
	try:
		RL = float(input('RL[ohm] = '));
	except ValueError:
		print('Wront input.');
		print('Enter z to close or press Enter to continue.');
		ch = input();
		continue;
	try:
		XL = float(input('XL[ohm] = '));
	except ValueError:
		print('Wront input.');
		print('Enter z to close or press Enter to continue.');
		ch = input();
		continue;
	try:
		Z0 = float(input('Z0[ohm] = '));
	except ValueError:
		print('Wront input.');
		print('Enter z to close or press Enter to continue.');
		ch = input();
		continue;	
	if (Z0 <= zero):
		print('Nominal impedance must be positive.');
		print('Enter z to close or press Enter to continue.');
		ch = input();
		continue;
	if ((RL / Z0) <= zero):
		print('Load resistance must be positive.');
		print('Enter z to close or press Enter to continue.');
		ch = input();
		continue;
	try:
		f = float(input(' f[Hz]  = '));
	except ValueError:
		print('Wront input.');
		print('Enter z to close or press Enter to continue.');
		ch = input();
		continue;
	if (f <= zero):
		print('Operating frequency must be positive.');
		print('Enter z to close or press Enter to continue.');
		ch = input();
		continue;
	print('\n---------------------');

	Y0 = 1.0 / Z0;
	GL = RL / (pow(RL, 2.0) + pow(XL, 2.0));
	BL = -XL / (pow(RL, 2.0) + pow(XL, 2.0));

	if ((((RL - Z0) / Z0) < -zero) and ((RL / Z0) > zero) and ((abs(GL - Y0) * Z0) > zero)):
		top = 1;																					# Serial element toward load.
		# First solution #
		X1 = -XL + math.sqrt(RL * (Z0 - RL));
		X2 = -(Z0 * RL) / (XL + X1);
		MatchingNetworkCalculation(X1, X2, B1, B2, f, top);
		# Second solution #
		X1 = -XL - math.sqrt(RL * (Z0 - RL));
		X2 = -(Z0 * RL) / (XL + X1);
		MatchingNetworkCalculation(X1, X2, B1, B2, f, top);
	if ((((GL - Y0) * Z0) < -zero) and ((GL * Z0) > zero) and ((abs(RL - Z0) / Z0) > zero)):
		top = 2;																					# Shunt element toward load.
		# First solution #
		B1 = -BL + math.sqrt(GL * (Y0 - GL));
		B2 = -(Y0 * GL) / (BL + B1);
		MatchingNetworkCalculation(X1, X2, B1, B2, f, top);
		# Second solution #
		B1 = -BL - math.sqrt(GL * (Y0 - GL));
		B2 = -(Y0 * GL) / (BL + B1);
		MatchingNetworkCalculation(X1, X2, B1, B2, f, top);
	if (((abs(RL - Z0) / Z0) <= zero) and (abs(XL / Z0) > zero)):
		top = 3;																					# RL = Z0
		# First solution #
		X1 = -XL;
		X2 = 0.0;
		# Second solution #
		B1 = -2.0 * BL;
		B2 = Y0 * GL / BL;
		MatchingNetworkCalculation(X1, X2, B1, B2, f, top);
	if (((abs(GL - Y0) * Z0) <= zero) and (abs(BL * Z0) > zero)):
		top = 4;																					# GL = Z0
		# First solution #
		B1 = -BL;
		B2 = 0.0;
		# Second solution #
		X1 = -2.0 * XL;
		X2 = Z0 * RL / XL;
		MatchingNetworkCalculation(X1, X2, B1, B2, f, top);
	if (((abs(RL - Z0) / Z0) <= zero) and (abs(XL / Z0) <= zero)):
		print('No matching network required.');
	print('Enter z to close or press Enter to continue.');
	ch = input();
	os.system('cls');
