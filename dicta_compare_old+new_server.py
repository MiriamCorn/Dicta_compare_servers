# in the file we get 2 versions of servers of common rhymes and determine:
# if the top 10 results of the old server are in the top 30 results of the new server
# if the top 10 results of the new server are in the top 30 results of the old server
# save in a dataframe
# next - see which words are missing

import requests
import pandas as pd
import json


def server_version(text, version):
    # this function returns the json data depending on the version of the server (old or new)
    if version == 'new':  # the new server

        json_data = {
            'soundplay_keyword': text,
            'rhyme_mode': 'half',
            'alit_num_of_lets': 2,
            'model': 'Rhyme',
            'soundplay_settings': {
                'allowletswap': True,
                'allowvocswap': True,
            },
            'semantic_keywords': [],
            'semantic_models': 'both',
            'tavnit_search': [],
            'morph_filter': {
                'pos': 0,
                'person': 0,
                'status': 0,
                'number': 0,
                'gender': 0,
                'tense': 0,
                'suffix_person': 0,
                'suffix_number': 0,
                'suffix_gender': 0,
            },
            'return_settings': {
                'min_syl': 1,
                'max_syl': 7,
                'accreturnsettings': 'matchinput',
                'returnpropernames': False,
                'ignoreLoazi': False,
                'baseOnly': False,
            },
        }

        response = requests.post('https://charuzit-4-0.loadbalancer.dicta.org.il/api', json=json_data)
        # response = requests.post('https://charuzit-3-0-test.loadbalancer.dicta.org.il/', json=json_data)  # test error
    else:  # the old server

        json_data = {
            "soundplay_keyword": text,
            "rhyme_mode": "half",
            "model": "rhyme",
            "ignoreLoazi": False,
            "baseOnly": False,
            "allowletswap": True,
            "allowvocswap": True,
            "semantic_diyuq": 0.75,
            "semantic_freq_thresh": 100,
            "semantic_models": "both",
            "multi_semantic_action": "default",
            "derive_exp": "immediate2nd",
            "fconflate_binyan": True,
            "min_syl": 1,
            "max_syl": 7,
            "alit_num_of_lets": 2,
            "semantic_keywords": [],
            "pos": 0,
            "person": 0,
            "status": 0,
            "number": 0,
            "gender": 0,
            "tense": 0,
            "has_suffix": "unk",
            "suffix_person": 0,
            "suffix_number": 0,
            "suffix_gender": 0,
            "accreturnsettings": "matchinput",
            "returnpropernames": False
        }

        response = requests.post('https://charuzit-3-0-test.loadbalancer.dicta.org.il/api',
                                 data=json.dumps(json_data, ensure_ascii=False).encode(encoding='utf-8'))

    response.raise_for_status()  # if an error occurs
    response_dict = response.json()

    return response_dict


def common_words_table_index(text, version):
    # given a word, a version of the server, find the table with the results of common rhymes.
    # return the index

    response_dict = server_version(text, version)  # get the json data

    for index, result in enumerate(response_dict["results"]):

        # loop through the list where each element is a 'table' (dictionary) of key value results
        # response_dict["results"] is a list (each element is a table)

        if result['mode'] == 'Rhyme_Common':
            print(f"table for common rhymes is index {index}")
            return index

    # This line is executed if the loop completes - the table does not exist
    raise ValueError("The table does not exist")


def common_words_table(text, index, version):
    # given a word, a version of server and the index
    # return the table of results for the word and index (in our case - common rhymes)

    response_dict = server_version(text, version)  # get the json data

    return response_dict["results"][index]


def top_results(table, text, size):
    # given a table and a word, get the top results in the table for the word
    # returns the top results as a list based on the given size. for old top 10. for new top 30

    print(f"top {size} results for the word: {text}")
    top = []

    for result in table["results"][0:size]:
        print(result['forms'][0])  # a word can have multiple forms, choose the first one
        top.append(result['forms'][0])

    return top


def compare_top_results(top_results_1, top_results_2):
    # given 2 lists of results, compare the lists

    if len(top_results_1) == len(top_results_2):
        list_size = len(top_results_1)
    else:
        print('list sizes are not the same')

    shared_results = list(set(top_results_1).intersection(set(top_results_2)))
    # list of items that appear in both lists
    prc = len(shared_results) / list_size  # the percentage of shared items

    print(f"The percentage of shared results is: {prc} \nThe number of shared results is: {len(shared_results)}")


def contain_all(top_results_old, top_results_new):
    # this function determines if all the results of the old server are contained in the new new server

    result = set(top_results_old).issubset(set(top_results_new))

    if result:

        print(f"The top {len(top_results_new)} results of the new server contains the top {len(top_results_old)} "
              f"results of the old server")
    else:
        common_elements = set(top_results_old).intersection(set(top_results_new))

        print(f"The top {len(top_results_new)} results of the new server contains only {len(common_elements)} "
              f"of the top {len(top_results_old)} old server")


def index_of_old_in_new(old_word, top_results_new):
    # given a word from the top results of the old server
    # return its index in the top results of the new server

    try:
        index = top_results_new.index(old_word)
        print(f"The index of the word {old_word} from the old server in the new server is {index}")

    except ValueError:
        print(f"The word {old_word} from the old server is not in the top {len(top_results_new)} of the new server")


def contain_word(new_word, top_results_old):
    # given a word from the top 10 results of new server
    # check if the top 10 results of old sever contain the word
    if new_word in top_results_old:
        print(f"The word {new_word} from the new server is in the top {len(top_results_old)} results of the old server")
    else:
        print(f"The word {new_word} from the new server is not in the top {len(top_results_old)} results of the old server")


if __name__ == "__main__":

    # words = ['יְדִידִי', 'בַּרְזֶל', 'שָׁלוֹם', 'גַּן', 'מִלְחָמָה', 'אֶרֶץ', 'דְּבַשׁ', 'יוֹנָה', 'פְּרִי', 'בַּיִת']
    words = ['יְדִידִי', 'בַּיִת']
    # words = ['יְדִידִי']

    word = 'יְדִידִי'

    old_common_rhyme_table_index = common_words_table_index(word,  version='old')  # get index of the table for old server
    # common_words_table(word, old_common_rhyme_table_index)

    new_common_rhyme_table_index = common_words_table_index(word, version='new')  # get index of the table for old new
    # common_words_table(word, new_common_rhyme_table_index)

    results_df = pd.DataFrame()

    size_top_old = 10  # the number of top results we want from the old server
    size_top_new = 30  # the number of top results we want from the new server

    for word in words:

        try:

            old_common_table = common_words_table(word, old_common_rhyme_table_index, version='old')
            # get the table of the results in common rhymes old server
            new_common_table = common_words_table(word, new_common_rhyme_table_index, version='new')
            # get the table of the results in common rhymes new server

            top_old_results = top_results(old_common_table, word, size_top_old)
            # find the top results in the table old server. return as a list
            top_new_results = top_results(new_common_table, word, size_top_new)
            # find the top results in the table new server. return as a list

            compare_top_results(top_old_results, top_new_results[0: size_top_old])  # because the size of new is bigger

            contain_all(top_old_results, top_new_results)  # new contains old

            for top_word in top_old_results:  # check for each word in the top results of old server

                index_of_old_in_new(top_word, top_new_results)  # top word of old in top words of new

            for top_word in top_new_results:  # check for each word in top results of new server

                contain_word(top_word, top_old_results)  # top word of new is in top words of old

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")

        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")

        except ValueError as e:  # table is not found
            print(e)

    # results_df.to_csv(f"Top results for the words.csv", encoding='utf-8')  # save all results in a csv file
