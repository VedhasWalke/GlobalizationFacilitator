/*
Main Algorithm Prototype

Date Updated: 11/24/20
Description:
- Naive Bayes Framework

Features:


*/

#include <iostream>
#include <vector>
#include <fstream>
#include <numeric>
using namespace std;

struct WordSet {
	vector<string> words;
	vector<int> counts;
	int numberOfClasses;
};


int main()
{
	

	// WordSet Neg = PositiveParse();
	// WordSet Pos = NegativeParse();
	// WordSet All = FullParse1();
	

	WordSet All;
	All.words = { "good", "bad", "is", "many", "delicious", "disgusting", "where", "people", "I", "food", "great", "terrible", "cooked", "eat", "gross", "dirty", "beautiful", "outdoor", "love", "hate"};
	All.counts = { 5, 8, 10, 7, 4, 3, 5, 2, 8, 18, 9, 17, 3, 2, 8, 2, 1, 1, 2, 8, 7};
	int N = size(All.words); // total number of words

	WordSet Pos;
	Pos.words = { "good", "is", "many", "delicious", "where", "people", "I", "love", "outdoor", "beautiful"};
	Pos.counts = { 1, 2, 3, 5, 6, 7, 1, 8, 1, 8 };
	Pos.numberOfClasses = 9; // there were 9 positive reviews

	WordSet Neg;
	Neg.words = { "bad", "is", "terrible", "dirty", "cooked", "gross", "hate", "eat"};
	Neg.counts = { 1, 2, 3, 5, 6, 7, 1, 8};
	Neg.numberOfClasses = 6; // there were 9 positive reviews



	vector<int> Pwp(N); // Probability of word given positive class 
	vector<int> Pwn(N); // Probability of word given negative class
	vector<int> Pw(N); // Probability of word
	int Pc[2]; // Probability of class
	
	// Pwp
	int sum = accumulate(Pos.counts.begin(), Pos.counts.end(), 0);
	for (int i = 0; i < N; i++)
		Pwp[i] = Pos.counts[i] / sum;
	
	// Pwn
	sum = accumulate(Neg.counts.begin(), Neg.counts.end(), 0);
	for (int i = 0; i < N; i++)
		Pwn[i] = Neg.counts[i] / sum;
	
	// Pw
	sum = accumulate(All.counts.begin(), All.counts.end(), 0);
	for (int i = 0; i < N; i++)
		Pw[i] = All.counts[i] / sum;

	// Pc
	Pc[0] = Neg.numberOfClasses / All.numberOfClasses;
	Pc[1] = Pos.numberOfClasses / All.numberOfClasses;
	
	


}

