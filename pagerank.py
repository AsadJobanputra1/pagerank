import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    for p in corpus:
        print(f"{p} links to: {corpus[p]}")
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    linkedPages = corpus[page]
    transitionModel = dict()
    
    """
    With probability damping_factor, the random surfer should randomly choose one of the 
    links from page with equal probability.
    """
    for p in linkedPages:
        transitionModel[p] = damping_factor*1/len(linkedPages)

    """
    With probability 1 - damping_factor, the random surfer should randomly choose one of 
    all pages in the corpus with equal probability.
    """
    randomSurferProbability = (1-damping_factor)/ (len(corpus))
    for p in corpus:
        if p in transitionModel:
            transitionModel[p] += randomSurferProbability
        else:
            transitionModel[p] = randomSurferProbability
    
    """
    If page has no outgoing links, then transition_model should return a probability 
    distribution that chooses randomly among all pages with equal probability. 
    (In other words, if a page has no links, we can pretend it has links to 
    all pages in the corpus, including itself.)
    """
    if len(linkedPages) == 0:
        transitionModel = dict()
        for p in corpus:
            transitionModel[p] = 1 / len(corpus)
    
    checkProbabilityDictionary(transitionModel)
    
    return transitionModel

def checkProbabilityDictionary(model):
    # test: sum of all distributions should be 1
    # test: each page should have distribution between 0 .. 1
    sumProbabilities = 0
    for p in model:
        if model[p] > 1 or model[p] < 0 : raise Exception ("probability not in bounds")
        sumProbabilities += model[p]
    if round(sumProbabilities,3) != 1.0 : 
        raise Exception (f"Sum probability {sumProbabilities} == 1\n")
        return False
    return True

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    estimatedSamplePageRank = dict()
    """
    The first sample should be generated by choosing from a page at random.
    """
    pageToSample = random.choice(list(corpus))
    estimatedSamplePageRank[pageToSample] = 1/n
    for i in range(1,n):
        """
        For each of the remaining samples, the next sample should be generated from the previous 
        sample based on the previous sample???s transition model.
        You will likely want to pass the previous sample into your transition_model function, 
        along with the corpus and the damping_factor, to get the probabilities for the next sample.
        For example, if the transition probabilities are {"1.html": 0.05, "2.html": 0.475, 
        "3.html": 0.475}, then 5% of the time the next sample generated should be "1.html", 
        47.5% of the time the next sample generated should be "2.html", and 47.5% of the time 
        the next sample generated should be "3.html".
        You may assume that n will be at least 1.
        """
        transitionModel = transition_model(corpus, pageToSample, damping_factor)
        
        pageToSample = random.choices(list(transitionModel.keys()),        weights=list(transitionModel.values()), k=1)[0]
        
        # increase count by (1/total-samples) to say we selected page
        if pageToSample in estimatedSamplePageRank:
            estimatedSamplePageRank[pageToSample] += 1/n 
        else:
            estimatedSamplePageRank[pageToSample] = 1/n 

        # next page to sample is one of the linked pages by 85% or any other page by 1-85%
        sampleMethod = random.choices(["sampleFromLinkedPage","sampleFromAllPages"],[damping_factor,1-damping_factor],k=1)[0]
        if sampleMethod == "sampleFromLinkedPage":
            pageToSample = random.choices(list(transitionModel.keys()), weights=list(transitionModel.values()), k=1)[0]
        else:
            pageToSample = random.choice(list(corpus))

        
    checkProbabilityDictionary(estimatedSamplePageRank)
    return  estimatedSamplePageRank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    iterativePageRank = dict()
    
    # The function should begin by assigning each page a rank of 1 / N, where N is the total number of pages in the corpus.
    
    for p in corpus:
        iterativePageRank[p] = 1/len(corpus)
    
    """
    The function should then repeatedly calculate new rank values based on all of the current rank values, according to the PageRank formula in the ???Background??? section. (i.e., calculating a page???s PageRank based on the PageRanks of all pages that link to it).
A page that has no links at all should be interpreted as having one link for every page in the corpus (including itself).
This process should repeat until no PageRank value changes by more than 0.001 between the current rank values and the new rank values.

    """
    #This process should repeat until no PageRank value changes
    # by more than 0.001 between the current rank values and the 
    # new rank values.
   
    # calculate incoming links
    incomingPages = dict()
    for page , linkedTo in corpus.items():
        for p in linkedTo:
            if p in incomingPages:
                incomingPages[p].append(page)
            else:
                incomingPages[p] = [page]
    
    pageRankChange = 1
    while(pageRankChange > 0.001):
        #select a page based on weighted probabilities
        #pageToSample = random.choices(list(iterativePageRank.keys()), cum_weights=list(iterativePageRank.values()), k=1)[0]
        #select page for all items
        pageRankChange = 0
        for pageToSample in corpus:
        
            newPageRank = (1 - damping_factor)/len(corpus) 
            
            #if page has no incoming pages
            if not pageToSample in incomingPages: continue
            
            for incomingPage in incomingPages[pageToSample]:
                newPageRank += damping_factor * iterativePageRank[incomingPage]/len(corpus[incomingPage])
            
            # calculate change in pageRank (absolute change)
            pageRankChange += abs(iterativePageRank[pageToSample] - newPageRank)
            iterativePageRank[pageToSample] = newPageRank        
        
        
    return iterativePageRank


if __name__ == "__main__":
    main()
