from os import listdir
from collections import defaultdict
import re



# subset data paths
sub_pos_test_path  = "data/subset/test/pos/"
sub_neg_test_path  = "data/subset/test/neg/"
sub_pos_train_path = "data/subset/train/pos/"
sub_neg_train_path = "data/subset/train/neg/"



stop_words_path = "data/stop_words.txt"



class Reviewer():
    # a has a training, and methods for evaluating reviews,
    # might also take directories as a parameter, both for stopwords, training data, and test data
    def __init__(self, p_training_data_path, n_training_data_path , p_test_data_path, n_test_data_path, sw_path, n_gram):
        self.p_train_path = p_training_data_path
        self.n_train_path = n_training_data_path
        self.p_test_data_path = p_test_data_path
        self.n_test_data_path = n_test_data_path
        self.n_gram = n_gram
        self.all_reviews_data = Review()
        self.positive_reviews_data = Review()
        self.negative_reviews_data = Review()

        # generates the list of stop words, and sorts the list
        stop_words_file = open(sw_path)
        s_w = []
        for l in stop_words_file:
            s_w.append(l.strip())
        s_w.sort()
        self.stop_words = s_w



    # implementation part 1
    def format_reviews(self, directory, n_gram):
        # performs basic read operations on all reviews in a directory, before they are evaluated, returns a list
        # of reviews, which has been set to lowercase and illegal characters, duplicates, and stop_words has been removed

        reviews = listdir(directory)
        list_of_reviews = []
        for i in reviews:
            current_review = open(directory + i)
            review_string = ''
            for l in current_review:
                review_string += self.make_legal_format(l)
            current_review_list = self.remove_duplicates(review_string)
            current_review_list = self.create_n_grams(current_review_list, n_gram)
            current_review_list = self.remove_stop_words(current_review_list)
            list_of_reviews.append(current_review_list)
            current_review.close()

        return list_of_reviews

    def make_legal_format(self,text):
        # makes the text lower case and alpha numerical.
        t = text.lower()
        t = re.sub(r'([^\s\w]|_)', '', t)

        return t


    def remove_duplicates(self, text):
        # function that creates a set from a list to remove duplicates
        # then returns the set as a list again
        t = list(set(text.split()))
        return t

    # implementation part 2: Find the 25 most common words for positive and negative reviews
    def find_most_common(self):
        pass


    # implementation part 3

    def remove_stop_words(self, word_list):
        # make the string into a list, remove duplicates, and remove stop words.
        t = word_list
        t_length = len(t)
        i = 0
        while i < (t_length):
            if t[i] in self.stop_words:
                t.remove(t[i])
                # both indexes needs to be subtracted from since the remaining indexes has changed.
                t_length -= 1
                i -= 1
            i+=1
        return t
    

    # implementation part 4 find information value: (done)

    def information_value(self, sub_set_prevalence, global_prevalence):
        info_value = defaultdict(float)
        for word in sub_set_prevalence.items():
            info_value[word[0]] = float(word[1]/(global_prevalence.get(word[0])))

        return info_value


    def find_prevalence_collection(self, reviews):
        number_of_reviews = len(reviews)
        pos_count = defaultdict(float)
        for review in reviews:
            for word in review:
                pos_count[word] += float(1.0)
        return pos_count


    # implementation part 5: Pruning (Done)

    # find prune words
    def make_prune_list(self, all_reviews, percent):
        total_size = len(all_reviews)
        global_prevalence = list(self.find_prevalence_collection(all_reviews).items())
        prune_list = []
        for i in global_prevalence:
            if float(i[1]/total_size) < percent:
                prune_list.append(i[0])
        return prune_list

    def prune(self, review_information_value, prune_words):
        # could also be done, before assigning information values, but uses a default dict, so it can be
        # useful to do it in this order
        review_words = review_information_value.copy()
        for word in prune_words:
            if word in review_words:
                review_words.pop(word)
        return review_words


    # implementation part 6: n_grams (Done)
    def create_n_grams(self, word_list, n_value):
        w_l = word_list
        n_grams = []
        if n_value not in [2,3]:
            raise Exception("Illegal length of n_gram")
        for i in range(len(w_l)- n_value + 1):
            current_word = '' + str(w_l[i])
            for n in range(1,n_value):
                current_word +='_' + str(w_l[i+n])
            n_grams.append(current_word)

        return w_l + n_grams


    def train_reviewer(self, prune_limit):
        generated_pos_reviews = self.format_reviews(self.p_test_data_path, self.n_gram)
        generated_neg_reviews = self.format_reviews(self.n_test_data_path, self.n_gram)

        self.all_reviews_data.set_reviews(generated_pos_reviews + generated_neg_reviews)
        self.positive_reviews_data.set_reviews(generated_pos_reviews)
        self.negative_reviews_data.set_reviews(generated_neg_reviews)

        # creating lists of prevalence of all words
        self.all_reviews_data.set_word_prevalence(self.find_prevalence_collection(self.all_reviews_data.get_reviews()))
        self.positive_reviews_data.set_word_prevalence(self.find_prevalence_collection(self.positive_reviews_data.get_reviews()))
        self.negative_reviews_data.set_word_prevalence(self.find_prevalence_collection(self.negative_reviews_data.get_reviews()))

        # assigning information_value to the words
        self.positive_reviews_data.set_info_values(self.information_value(self.positive_reviews_data.get_word_prevalence(),
                                                                          self.all_reviews_data.get_word_prevalence()))

        self.negative_reviews_data.set_info_values(self.information_value(self.negative_reviews_data.get_word_prevalence(),
                                                                          self.all_reviews_data.get_word_prevalence()))
        # generates prune words
        prune_words = self.make_prune_list(self.all_reviews_data.get_reviews(), prune_limit)

        print(len(self.positive_reviews_data.get_info_values()))
        print(len(self.negative_reviews_data.get_info_values()))

        # prune
        self.positive_reviews_data.set_info_values(self.prune(self.positive_reviews_data.get_info_values(), prune_words))
        self.negative_reviews_data.set_info_values(self.prune(self.negative_reviews_data.get_info_values(), prune_words))

        # Training done

    def review(self):
        positive_test_reviews = self.format_reviews(self.p_test_data_path, self.n_gram)
        negative_test_reviews = self.format_reviews(self.n_test_data_path, self.n_gram)



class Review():
    def __init__(self):
        self.reviews = []
        self.info_values = None
        self.number_of_reviews = 0
        self.word_prevalence = None

    def set_reviews(self, reviews):
        self.reviews = reviews
        self.number_of_reviews = len(self.reviews)

    def get_reviews(self):
        return self.reviews

    def set_info_values(self, info_values):
        self.info_values = info_values

    def get_info_values(self):
        return self.info_values

    def set_word_prevalence(self, word_prevalence):
        self.word_prevalence = word_prevalence

    def get_word_prevalence(self):
        return self.word_prevalence

rew = Reviewer(sub_pos_train_path, sub_neg_train_path, sub_pos_test_path, sub_neg_test_path, stop_words_path)
rew.train_reviewer(0.01)
# p_training_data_path, n_training_data_path , p_test_data_path, n_test_data_path, sw_path