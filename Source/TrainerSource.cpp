/*
Trainer System

Date Updated: 3/14/21

Description:
	Machine learning training algorithm based on Naive Bayes Framework.
	Uses two main data sets of customer reviews of a business: positive reviews
	and negative reviews. Furthermore, uses two auxilary datasets of highly specific,
	hand-picked data on the loyalty of a consumer based on review. Outputs file
	containing computed optimal features in special format as detailed in
	"ParametersFormat.txt" file in "Help" directory.

Non-primitive Data Types:
	vector<word>: a struct housing multiple variables key to analyzing a set of reviews.
		counts: vector storing number of instances of each word in all reviews of the vector<word>.
		pcounts: vector storing number of instances of each word in all positive reviews of the vector<word>.
		ncounts: vector storing number of instances of each word in all negative reviews of the vector<word>.
		numberOfmembers: number of words contained in a vector<word>, equivalent to size of counts vector.

Powerful Features:
		- Puts all reviews on the same scale(different people may generally rate stores differently; each person
		  has a different sense of a 3 star service, for example. Looking at the content and sentiment of the
		  review gives a better measure of how much the reviewer liked the service as opposed to other reviewers.
		- Converts discrete 5 stars to a continuous range
		- Loyal/Novel cannot be found without seperate hand-picked sets; we have measures for these qualities
		  as well.

Functions:
	Union: combines two vector<word>s(positive and negative in this case) into one.
	Compress: converts raw words into a word set.
	OutputFile: outputs parameters found in a text document

*/

#include <iostream>
#include <vector>
#include <fstream>
#include <numeric>
#include <string>
#include <algorithm>
#include <ctime>
#include <iterator>
using namespace std;


struct counts {
	int p; // positive counts
	int n; // negative counts
	int o; // novel counts
	int l; // loyal counts
};

struct word {
	string text;
	counts count;
	int value;
};



// Global Variables
ofstream Log;
int SetType; // 0 -> positive, 1 -> negative, 2 -> novel, 3 -> loyal
bool newSentenceFlag;
bool negationFlag;
int punctuationCounts[4][3];
int OtherData[4][7] = { { 0,0,0,0 }, { 0,0,0,0 }, { 0,0,0,0 }, {0,0,0,0} };
//		Rows: (0)uniqueWordCount, (1)rawWordCount, (2)numPosReviews, (3)ngramSize
//	 Columns: (0)p, (1)n, (2)o, (3)l, (4), (5), (6)trash 




// Constants
const string AbsPath = "C:\\Users\\750010316\\Documents\\GFacil\\GlobalizationFacilitator\\AlgorithmFiles\\TRAINER\\";
const string LogFileName = "Log.txt";
const string ParamFolderName = "ModelParameters\\";
const string posDataFileName = "TrainingSets\\PosTrainingSet\\PosTrainingSet.txt";
const string negDataFileName = "TrainingSets\\NegTrainingSet\\NegTrainingSet.txt";
const string novDataFileName = "TrainingSets\\NovTrainingSet\\NovTrainingSet.txt";
const string loyDataFileName = "TrainingSets\\LoyTrainingSet\\LoyTrainingSet.txt";
const string metadataFolderName = "Metadata\\";

// Metadata
string delimiter;
string taboo_chars;
vector<string> taboo_words;
vector<string> stop_words;
vector<string> negation_words;


// Prototypes
vector<word> ProcessDocument(string filename, int ngram);
string Preprocess(string raw_word);
vector<word> Union(vector<vector<word>> All);
vector<word> Compress(vector<string> raw_words);
vector<word> Trim(vector<vector<word>> All);
int Evaluate(counts c, int SetType);
void OutputFile(vector<word>::iterator pnbeg, vector<word>::iterator pnend, vector<word>::iterator olbeg, vector<word>::iterator olend);







string getDate() {
	time_t rawtime;
	struct tm timeinfo;
	char buffer[80];



	time(&rawtime);
	localtime_s(&timeinfo, &rawtime);

	strftime(buffer, sizeof(buffer), "%m-%d-%Y %H:%M:%S", &timeinfo);
	string str(buffer);
	return str;
}


vector<word> ProcessDocument(string filename, int ngram) {

	ifstream inputFile;
	inputFile.open(filename);

	// CHECK
	if (inputFile) {
		Log.open(AbsPath + LogFileName, ostream::out | ostream::app);
		Log << getDate() << " | " << filename.substr(filename.find_last_of('\\') + 1) << " opened successfully " << endl;
		Log.close();
	}
	else {
		Log.open(AbsPath + LogFileName, ostream::out | ostream::app);
		Log << getDate() << " | ERROR: Filename invalid |" << filename.substr(filename.find_last_of('\\') + 1) << " did not opened successfully" << endl;
		Log.close();
	}


	vector<string> raw_words, refined_phrases;
	string phrase, temp;
	vector<vector<word>> All(ngram);

	while (inputFile) {
		inputFile >> temp;
		raw_words.push_back(temp);
	}


	// adding some OtherData
	OtherData[1][SetType] = raw_words.size();
	OtherData[3][SetType] = ngram;
	for (int i = 0; i < raw_words.size(); i++) {
		if (raw_words[i] == delimiter)
			OtherData[2][SetType]++;
	}



	for (int n = 1; n <= ngram; n++) {
		int i = 0;
		refined_phrases.clear();

		negationFlag = false;
		newSentenceFlag = true;

		for (int i = 0; i < raw_words.size(); i++) {
			raw_words[i] = Preprocess(raw_words[i]);
		}


		while (i < raw_words.size() - n) {
			phrase = "";
			for (int j = 0; j < n; j++) {
				string phrase2 = raw_words[i + j];
				if (!any_of(taboo_words.begin(), taboo_words.end(), [phrase2](string s) {return s == phrase2;}))
					phrase += " " + raw_words[i + j];
				else{					
					j--;
					i++;
				}
			}
			phrase.erase(phrase.begin());


			if (phrase.find(delimiter) != string::npos) {
				i += n;
				continue;
			}


			/*
			int index = 0;
			int index2 = 0;

			phrase = "Wher to going";
			n = 3;

			string phrase2 = phrase + " ";
			phrase = "";
			for (int k = 0; k < n; k++) {
				index2 = phrase2.find(" ", index+1);
				phrase += Preprocess(phrase2.substr(index, index2-index));
				index = index2;
			}
			//phrase.erase(phrase.end() - 1);
			refined_phrases.push_back(phrase);
			*/
			refined_phrases.push_back(phrase);
			i++;
		}
		All[n - 1] = Compress(refined_phrases);
	}


	return Union(All);


}


string Preprocess(string raw_word) {

	//deleting taboo characters as defined by "taboo_chars" array
	size_t t = raw_word.find_first_of(taboo_chars);
	while (t != string::npos) {
		raw_word.erase(t);
		t = raw_word.find_first_of(taboo_chars);
	}


	if (raw_word == "a") {
		cout << "Ok";
	}

	



	// deleting stopwords
	string raw_word2 = raw_word;
	for (int i = 0; i < raw_word2.size(); i++) { raw_word2[i] = tolower(raw_word2[i]); }
	raw_word2.insert(raw_word2.begin(), ' ');
	raw_word2.insert(raw_word2.end(), ' ');
	for (int i = 0; i < stop_words.size(); i++) {
		t = raw_word2.find(" " + stop_words[i] + " ");
		if (t != string::npos)
			raw_word.erase(t, t + stop_words[i].size());
	}
	

	if (raw_word == delimiter) {
		negationFlag = false;
	}


	// append _NOT if negationFlag is up
	if (negationFlag) {
		raw_word = raw_word + "_NOT";
	}
	else {
		// search for negation words
		raw_word2 = raw_word;
		for (int i = 0; i < raw_word2.size(); i++) { raw_word2[i] = tolower(raw_word2[i]); }
		raw_word2.insert(raw_word2.begin(), ' ');
		raw_word2.insert(raw_word2.end(), ' ');
		for (int i = 0; i < negation_words.size(); i++) {
			t = raw_word2.find(" " + negation_words[i] + " ");
			if (t != string::npos) {
				raw_word.erase(t, t + negation_words[i].size());
				negationFlag = true;
			}
		}
		
	}

	



	// lowercase if newSentence
	if (newSentenceFlag) {
		raw_word[0] = tolower(raw_word[0]);
		newSentenceFlag = false;
	}

	if (raw_word == delimiter) {
		newSentenceFlag = true;
	}


	// checking for punctuation
	for (int i = 0; i < raw_word.size(); i++) {
		
		if (raw_word[i] == '.') {
			punctuationCounts[SetType][0]++;
			raw_word.erase(i);
			newSentenceFlag = true;
			negationFlag = false;
		}
		else if (raw_word[i] == '!') {
			punctuationCounts[SetType][1]++;
			raw_word.erase(i);
			newSentenceFlag = true;
			negationFlag = false;
		}
		else if (raw_word[i] == '?') {
			punctuationCounts[SetType][2]++;
			raw_word.erase(i);
			newSentenceFlag = true;
			negationFlag = false;
		}
		else {
			i++;
		}
		i--; // if punctuation char was deleted
	}

	

	return raw_word;
}


vector<word> Union(vector<vector<word>> All) { // lazily coded, kinda slow
	vector<word> c = All[0];

	// combining all vectors into one
	for (int i = 1; i < All.size(); i++) {
		c.insert(c.end(), All[i].begin(), All[i].end());
	}

	// sorting
	sort(c.begin(), c.end(), [](word a, word b) {return a.text < b.text; });

	int num = 0;
	vector<word> cset;
	// combining adjacent words into one
	for (int i = 0; i < c.size() - 1; i++) {

		if (c[i].text == c[i + 1].text) {
			num++;
		}
		else {
			int p = 0;
			int n = 0;
			int o = 0;
			int l = 0;

			for (int j = i; j >= i - num; j--) {
				p += c[j].count.p;
				n += c[j].count.n;
				o += c[j].count.o;
				l += c[j].count.l;
			}

			cset.push_back(word{ c[i].text,{p,n,o,l}, 1});
		}
	}

	OtherData[0][SetType] = cset.size();
	return cset;
}


vector<word> Compress(vector<string> raw_words) { // CHECK
	/*
	sort(raw_words.begin(), raw_words.end());

	int count = 1;
	string text = "";
	vector<word> set;

	text = raw_words[0];
	for (int i = 1; i < raw_words.size(); i++) {
		if (raw_words[i] == text) {
			count++;
		}
		else {

			counts c = { 0,0,0,0 };
			if (SetType == 0)
				c.p = count;
			else if (SetType == 1)
				c.n = count;
			else if (SetType == 2)
				c.o = count;
			else if (SetType == 3)
				c.l = count;

			set.push_back(word{ text, c, 0}); // correct struct declaration?
			count = 1;
			text = raw_words[i];
		}
	}



	// Erasing unwanted words {"" , "_NOT"}
	for (int i = 0; i < taboo_words.size(); i++) {
		string taboo_word = taboo_words[i];
		vector<word>::iterator index = find_if(set.begin(), set.end(), [taboo_word](word a) {return a.text == taboo_word; });
		if (index != set.end()) {
			set.erase(index);
		}
	}
	*/
	vector<word> set;
	for (int i = 0; i < raw_words.size(); i++){
		set.push_back(word{raw_words[i], 1, 0 });
	}

	return set;
}

int Evaluate(counts c, int SetType) {
	if (SetType == 6)
		return abs(c.p - c.n);
	else if (SetType == 7)
		return abs(c.o - c.l);

}

// temporary trimming --> lopping off bottom half
void Trim(vector<word> &All) {

	for (vector<word>::iterator j = All.begin(); j < All.end(); j++) {
		Evaluate((*j).count,SetType);
	}
	sort(All.begin(), All.end(), [](word a, word b) {return a.value < b.value; }); // sorting in correct order?

	All.erase(All.begin() + (All.size())/ 2, All.end()); // how much to trim?? (rn just lopping off bottom half values)


}


void OutputFile(vector<word>::iterator pnbeg, vector<word>::iterator pnend, vector<word>::iterator olbeg, vector<word>::iterator olend) {

	ofstream outf;

	// First Parameters File: Positive-Negative Word Counts
	outf.open(AbsPath + ParamFolderName + "Param1.txt");

	// Preliminary Information
	outf << "Parameters for Prediction\n";
	outf << "(";
	outf << "Positive-Negative";
	outf << ")\n";
	outf << "<text> [p] [n]\n";
	outf << "Last Modified: " << getDate() << "\n";
	outf << "#" << "\n"; // Data Starts Here

	// Recording Word Counts
	for (; pnbeg < pnend; pnbeg++) {
		outf << (*pnbeg).text << " " << (*pnbeg).count.p << " " << (*pnbeg).count.n << endl;
	}

	outf << "#";
	outf.close();

	// Second Parameters File: Novel-Loyal Word Counts
	outf.open(AbsPath + ParamFolderName + "Param2.txt");

	// Preliminary Information
	outf << "Parameters for Prediction\n";
	outf << "(";
	outf << "Novel-Loyal";
	outf << ")\n";
	outf << "<text> [o] [l]\n";
	outf << "Last Modified: " << getDate() << "\n";
	outf << "#" << "\n"; // Data Starts Here

	// Recording Word Counts
	for (; olbeg < olend; olbeg++) {
		outf << (*olbeg).text << " " << (*olbeg).count.o << " " << (*olbeg).count.l << endl;
	}

	outf << "#";

	outf.close();




	// Third Parameter File: Qualities of Word Counts
	outf.open(AbsPath + ParamFolderName + "Param3.txt");
	outf << "Parameters for Prediction\n";
	outf << "(Class Probability and Sums Data)\n";
	outf << "Last Modified: " << getDate() << "\n";
	outf << "#" << "\n"; // Data Starts Here

	for (int i = 0; i < 4; i++) {
		for (int j = 0; j < 4; j++) {
			outf << OtherData[i][j] << " ";
		}
		outf << "\n";
	}

	outf << "\n\n";

	for (int i = 0; i < 4; i++) {
		for (int j = 0; j < 3; j++) {
			outf << punctuationCounts[i][j] << " ";
		}
		outf << "\n";
	}

	outf << "#";
	outf.close();

	Log.open(AbsPath + LogFileName, ostream::out | ostream::app);
	Log << getDate() << " | Training Completed\n\n";


	// Third Parameter File: 

}













int main() {

// Setup

	Log.open(AbsPath + LogFileName, ostream::out | ostream::app);

	for (int i = 0; i < 4; i++) {
		for (int j = 0; j < 3; j++) {
			punctuationCounts[i][j] = 0;
		}
	}
	
	newSentenceFlag = true;

	negationFlag = false;

	ifstream inFile;
	string temp;
	vector<string> taboo_chars2;
	inFile.open(AbsPath + metadataFolderName + "Delimiter.txt");
	inFile >> delimiter;
	inFile.close();
	inFile.open(AbsPath + metadataFolderName + "StopWordList2.txt");
	while (inFile) {
		inFile >> temp;
		stop_words.push_back(temp);
	}
	stop_words.erase(stop_words.end()-1); // repeated elem at end
	inFile.close();
	inFile.open(AbsPath + metadataFolderName + "NegationWords.txt");
	while (inFile) {
		inFile >> temp;
		negation_words.push_back(temp);
	}
	negation_words.erase(negation_words.end()-1);
	inFile.close();
	inFile.open(AbsPath + metadataFolderName + "TabooChars.txt");
	while (inFile) {
		inFile >> temp;
		taboo_chars2.push_back(temp);
	}
	taboo_chars2.erase(taboo_chars2.end()-1);
	inFile.close();
	taboo_chars = "";
	for (int i = 0; i < taboo_chars2.size(); i++) {
		taboo_chars = taboo_chars + taboo_chars2[i];
	}
	inFile.open(AbsPath + metadataFolderName + "TabooWords.txt");
	taboo_words.push_back("");
	while (inFile) {
		inFile >> temp;
		taboo_words.push_back(temp);
	}
	taboo_words.erase(taboo_words.end() - 1);
	inFile.close();


// Positive/Negative Training
	SetType = 0;
	vector<word> Pos = ProcessDocument(AbsPath + posDataFileName, 2);
	SetType = 1;
	vector<word> Neg = ProcessDocument(AbsPath + negDataFileName, 2);
	SetType = 2;
	vector<word> Nov = ProcessDocument(AbsPath + novDataFileName, 3);
	SetType = 3;
	vector<word> Loy = ProcessDocument(AbsPath + loyDataFileName, 3);
	SetType = 6;
	vector<word> PosNeg = Union({ Pos, Neg });
	Trim(PosNeg);
	SetType = 7;
	vector<word> NovLoy = Union({ Nov, Loy });
	Trim(NovLoy);






	// OtherData: PcPos  PcNeg  sum  psum  nsum numberOfmembers

	OutputFile(PosNeg.begin(), PosNeg.end(), NovLoy.begin(), NovLoy.end());

}

