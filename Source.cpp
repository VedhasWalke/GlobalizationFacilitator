/*
Poker Hands
Author: Vedhas Walke
Date: 11/3/20
Description: Find the winner given two different poker hands
			 according to the following highest to lowerst 
			 classification:
			 
			 0) Straight Flush
			 1) Four of a Kind
			 2) Full House
			 3) Flush
			 4) Straight
			 5) Three of a Kind
			 6) Two Pairs
			 7) Pair
			 8) High Card

			 If there is a tie in this hierarchy, then the winner
			 is the one with the highest card(resolving tiesvaries 
			 slightly in each category).
*/

// 2H 3H 4H 5H 6H AC AS AD AH KH

#include <iostream>
#include <algorithm>
using namespace std;

// Global Variables
int Vals[2][5];
char Suits[2][5];
	// 0 -> black
	// 1 -> white
bool cat[9]; // which categories does this set fall into?


// Helper Functions
int IndexOfThreePair(int N) {
	for (int i = 0; i < 3; i++) {
		if (Vals[N][i] == Vals[N][i + 1] && Vals[N][i + 1] == Vals[N][i + 2])
			return i;
	}
	return 5;
}

int IndexOfMthTwoPair(int N, int M) {
	int counter = 0;
	int index = 4;
	while (counter < M) { // assumes that M < number of pairs (otherwise program will crash)
		if (Vals[N][index] == Vals[N][index - 1])
			counter++;
		index--;
	}
	return index;
}

int IndexOfMthSingle(int N, int M) {
	int counter = 0;
	int index = 5;
	while (counter < M) {
		index--;
		if ((index != 0 && index != 4 && Vals[N][index] != Vals[N][index - 1] && Vals[N][index] != Vals[N][index + 1]) || (index == 0 && Vals[N][index] != Vals[N][index + 1]) || (index == 4 && Vals[N][index] != Vals[N][index - 1]))
			counter++;
	}
	return index;
}

bool DontRun(int category) {
	int highest;
	for (int i = 0; i < 9; i++) {
		if (cat[i] == 1) {
			highest = i;
			break;
		}
	}
	if (category <= highest)
		return false;
	return true;
}



// Resolve Ties in Heirarchy
int BreakTie(int category, int level) { // first level is 4
	
	if (Vals[0][0] == Vals[1][0] && Vals[0][1] == Vals[1][1] && Vals[0][2] == Vals[1][2] && Vals[0][3] == Vals[1][3] && Vals[0][4] == Vals[1][4])
		return 2;

	if (level < 0)
		return 2;
	
	if (category == 0 || category == 3 || category == 4 || category == 8) {
		// Highest to lowest comparing
		if (Vals[0][level] > Vals[1][level])
			return 0;
		else if (Vals[0][level] < Vals[1][level])
			return 1;
		else
			return BreakTie(category, level - 1);
		
	}
	else if (category == 2 || category == 5) {
		int B = Vals[0][IndexOfThreePair(0)]; // current black
		int W = Vals[1][IndexOfThreePair(1)]; // current white
		if (B > W)
			return 0;
		else if (W > B)
			return 1;
		else if (category == 2)
			return BreakTie(6, 1);
		else if (category == 5)
			return BreakTie(9, 4);
	}
	else if (category == 1) {
		int W, B;

		if (Vals[0][0] == Vals[0][1])
			B = Vals[0][0];
		else
			B = Vals[0][4];
		
		if (Vals[1][0] == Vals[1][1])
			W = Vals[1][0];
		else
			W = Vals[1][4];

		if (B > W)
			return 0;
		else if (W > B)
			return 1;
		else
			return BreakTie(9, 4);

	
	}
	else if (category == 6 || category == 7){
		int B = Vals[0][IndexOfMthTwoPair(0, 5-level)]; // level may be wrong
		int W = Vals[1][IndexOfMthTwoPair(1, 5-level)];

		if (B > W)
			return 0;
		else if (W > B)
			return 1;
		else if (category == 6 && level != 3)
			return BreakTie(6, level - 1);
		else
			return BreakTie(9, 4);

	}
	else if (category == 9){
	// Compare single elements only
		int B = Vals[0][IndexOfMthSingle(0, 5-level)];
		int W = Vals[1][IndexOfMthSingle(1, 5-level)];
		
		if (B > W)
			return 0;
		else if (W > B)
			return 1;
		else
			return BreakTie(9, level - 1);

	}

	
}



// Determine Heirarchical Position
int FindHighestCategory(int N) {
	for (int i = 0; i < 8; i++) // resetting cat array
		cat[i] = 0;

	cat[8] = 1;
	sort(Vals[N], Vals[N] + 5);

	// Four of a Kind
	int counter = 0;
	int firstVal = Vals[N][0];
	for (int i = 1; i < 5; i++) {
		if (Vals[N][i] != firstVal)
			counter++;
	}
	if (counter == 1)
		cat[1] = 1;
	else if (counter == 4) {
		cat[1] = 1;
		firstVal = Vals[N][1];
		for (int i = 2; i < 5; i++) {
			if (Vals[N][i] != firstVal) {
				cat[1] = 0;
				break;
			}
		}
	}


	// Flush
	if (!DontRun(3)) {
		cat[3] = 1;
		char commonSuit = Suits[N][0];
		for (int i = 1; i < 5; i++) {
			if (Suits[N][i] != commonSuit) {
				cat[3] = 0;
				break;
			}
		}
	}

	// Straight
		// assuming array is sorted
	
		cat[4] = 1;
		for (int i = 1; i < 5; i++) {
			if (Vals[N][i] != Vals[N][i - 1] + 1) {
				cat[4] = 0;
				break;
			}
		}
	

	// Straight Flush
	if (cat[3] && cat[4])
		cat[0] = 1;

	// Full House
	if (!DontRun(2)) {
		int subArr1a[3] = { Vals[N][2], Vals[N][3], Vals[N][4] };
		int subArr1b[2] = { Vals[N][0], Vals[N][1] };
		int subArr2a[3] = { Vals[N][0], Vals[N][1], Vals[N][2] };
		int subArr2b[2] = { Vals[N][3], Vals[N][4] };
		if ((subArr1a[0] == subArr1a[1] && subArr1a[1] == subArr1a[2] && subArr1b[0] == subArr1b[1]) || (subArr2a[0] == subArr2a[1] && subArr2a[1] == subArr2a[2] && subArr2b[0] == subArr2b[1]))
			cat[2] = 1;
	}

	// Pair
	if (!DontRun(6)) {
		if (Vals[N][0] == Vals[N][1]) {
			int subArr[3] = { Vals[N][2], Vals[N][3], Vals[N][4] };

			if (subArr[0] == subArr[1] || subArr[1] == subArr[2])
				cat[6] = 1; // Two Pairs
			else
				cat[7] = 1;
		}
		else if (Vals[N][1] == Vals[N][2]) {
			int subArr[3] = { Vals[N][0], Vals[N][3], Vals[N][4] };
			if (subArr[0] == subArr[1] || subArr[1] == subArr[2])
				cat[6] = 1; // Two Pairs
			else
				cat[7] = 1;
		}
		else if (Vals[N][2] == Vals[N][3]) {
			int subArr[3] = { Vals[N][0], Vals[N][1], Vals[N][4] };
			if (subArr[0] == subArr[1] || subArr[1] == subArr[2])
				cat[6] = 1; // Two Pairs
			else
				cat[7] = 1;
		}
		else if (Vals[N][3] == Vals[N][4]) {
			int subArr[3] = { Vals[N][0], Vals[N][1], Vals[N][2] };
			if (subArr[0] == subArr[1] || subArr[1] == subArr[2])
				cat[6] = 1; // Two Pairs
			else
				cat[7] = 1;
		}
	}

	// Three of a Kind
	counter = 0;
	if (!DontRun(5)) {
		if (Vals[N][0] == Vals[N][1] && Vals[N][1] == Vals[N][2] || Vals[N][1] == Vals[N][2] && Vals[N][2] == Vals[N][3] || Vals[N][2] == Vals[N][3] && Vals[N][3] == Vals[N][4])
			cat[5] = 1;
	}


	// Finding highest category
	for (int i = 0; i < 9; i++) {
		if (cat[i] == 1)
			return i;
	}

}



int main() {
	
	while(1) {
		// Inputting Cards
		char temp;
		for (int i = 0; i < 5; i++) {
			cin.get(temp);
			if (temp > '0' && temp <= '9')
				Vals[0][i] = temp - '0';
			else if (temp == 'T')
				Vals[0][i] = 10;
			else if (temp == 'J')
				Vals[0][i] = 11;
			else if (temp == 'Q')
				Vals[0][i] = 12;
			else if (temp == 'K')
				Vals[0][i] = 13;
			else if (temp == 'A')
				Vals[0][i] = 14;

			cin.get(Suits[0][i]);
			cin.get(temp);
		}

		for (int i = 0; i < 5; i++) {
			cin.get(temp);
			if (temp > '0' && temp <= '9')
				Vals[1][i] = temp - '0';
			else if (temp == 'T')
				Vals[1][i] = 10;
			else if (temp == 'J')
				Vals[1][i] = 11;
			else if (temp == 'Q')
				Vals[1][i] = 12;
			else if (temp == 'K')
				Vals[1][i] = 13;
			else if (temp == 'A')
				Vals[1][i] = 14;

			cin.get(Suits[1][i]);
			cin.get(temp);
		}

		int blackHigh = FindHighestCategory(0);
		int whiteHigh = FindHighestCategory(1);

		if (blackHigh < whiteHigh)
			cout << "Black wins.\n";
		else if (blackHigh > whiteHigh)
			cout << "White wins.\n";
		else
		{
			int winner = BreakTie(blackHigh, 4);
			if (winner == 0)
				cout << "Black wins.\n";
			else if (winner == 1)
				cout << "White wins.\n";
			else
				cout << "Tie.\n";
		}

	}

	

	return 0;

}