#!/bin/bash
    # file: enron_naive_bayes.sh
    # description: trains a simple one-word naive bayes spam
    # filter using enron email data
    # usage: ./enron_naive_bayes.sh <word>
    # requirements:
    #    wget
    #
    # author: jake hofman (gmail: jhofman)
    # how to use the code
    if [ $# -eq 1 ]
    then
        word=$1
    else
        echo "usage: enron_naive_bayes.sh <word>"
        exit
    fi

     ### PART 1
    if ! [ -e enron1.tar.gz ]
    then
        wget 'http://www.aueb.gr/users/ion/data/enron-spam/preprocessed/enron1.tar.gz'
    fi

    if ! [ -d enron1 ]
    then
        tar zxvf enron1.tar.gz
    fi

    cd enron1

    ### PART 2
    Nspam=`ls -l spam/*.txt | wc -l`
    Nham=`ls -l ham/*.txt | wc -l`
    Ntot=$Nspam+$Nham
    echo $Nspam spam examples
    echo $Nham ham examples

    Nword_spam=`grep -il $word spam/*.txt | wc -l`
    Nword_ham=`grep -il $word ham/*.txt | wc -l`
    echo $Nword_spam "spam examples containing $word"
    echo $Nword_ham "ham examples containing $word"

    ### PART 3
    Pspam=`echo "scale=4; $Nspam / ($Nspam+$Nham)" | bc`
    Pham=`echo "scale=4; 1-$Pspam" | bc`
    echo
    echo "estimated P(spam) =" $Pspam
    echo "estimated P(ham) =" $Pham
    Pword_spam=`echo "scale=4; $Nword_spam / $Nspam" | bc`
    Pword_ham=`echo "scale=4; $Nword_ham / $Nham" | bc`

    echo "estimated P($word|spam) =" $Pword_spam
    echo "estimated P($word|ham) =" $Pword_ham

    ### PART 4
    Pham_word=`echo "scale=4; $Pword_ham*$Pham" | bc`
    Pspam_word=`echo "scale=4; $Pword_spam*$Pspam" | bc`
    Pword=`echo "scale=4; $Pspam_word+$Pham_word" | bc`
    Pspam_word=`echo "scale=4; $Pspam_word / $Pword" | bc`
    echo
    echo "P(spam|$word) =" $Pspam_word
    cd ..


