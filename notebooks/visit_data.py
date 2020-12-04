# can we predict the next site to be visited from the current site?
# this is a hard high cardinality challenge, so at random, the predictive performance is low
# is this flawed anyway, as the results being presented just reflect what the user was limited to selecting
# like predicting that the bus is red
# have a performance measurement at random, and using the model results
# are the parent pagePaths sufficiently granular

import pandas as pd
import os
import numpy as np
import re
from flatten_dict import unflatten, flatten

DATA_DIR = 'data/'

# downloaded data from bigquery, using sql beneath
'''
SELECT
date, fullVisitorId, visitId, hits.hour, hits.minute, hits.hitNumber, hits.page.pagePath, hits.page.pageTitle
FROM `govuk-bigquery-analytics.87773428.ga_sessions_20201113`, unnest(hits) as hits
WHERE hits.type = "PAGE" and hits.hour = 12
Limit 10000000
'''
visit_data = pd.read_csv(DATA_DIR + "bq-results-20201116-153658-4lgqv331oo43.csv")
visit_data.shape

# there is data sorting issue as seen here
visit_data[visit_data['fullVisitorId'] == 3250250007886851499]

# sort by fullVisitorId, visitId, hour, minute, hitNumber
visit_data = visit_data.sort_values(by=['fullVisitorId', 'visitId', 'hour', 'minute', 'hitNumber'])
visit_max = visit_data.groupby('fullVisitorId')['fullVisitorId'].count()
visit_max = pd.DataFrame({'fullVisitorId': visit_max.index.to_list(),
                          'visit_max': visit_max.to_list()})
visit_counts = visit_max['visit_max'].value_counts()
# we can see that in fact only 99% of users have a max session count of 20
# 90% have total of 5
sum(visit_counts[:5]) / sum(visit_counts)
# 73% have total of 2
sum(visit_counts[:2]) / sum(visit_counts)
# 53% have total of 1
sum(visit_counts[:1]) / sum(visit_counts)

# model for entries where there is at least a lag 1 path, but only consider the previous link
# could extend this for additional lags later, but stick to lag 1 for the moment
visit_data_reduced = visit_data.merge(right=visit_max, on='fullVisitorId', how='inner')
visit_data_reduced.shape
visit_data_reduced[visit_data_reduced['fullVisitorId'] == 3250250007886851499]

# remove about 20% of data as the visit was only one URL
visit_data_reduced = visit_data_reduced[visit_data_reduced['visit_max'] > 1]
visit_data_reduced.shape


def clean_prefix(pagePath_string,
                 prefix_remove=['guidance/', 'collections/', 'government/', 'help/',
                                'organisations/', 'publications/', 'browse/', 'news/', 'topic/']):
    '''
    clean the listed prefixes from the pagePath
    '''
    for prefix in prefix_remove:
        prefix_location = pagePath_string.find(prefix)
        if prefix_location >= 0:
            pagePath_string = pagePath_string[(len(prefix) + prefix_location):]
    return pagePath_string


visit_data_reduced['pagePath_clean'] = [clean_prefix(p) for p in visit_data_reduced['pagePath']]
fields_of_interest = ['fullVisitorId', 'visitId', 'hour', 'minute', 'pagePath', 'pagePath_clean']
visit_data_reduced[visit_data_reduced['fullVisitorId'] == 3250250007886851499][fields_of_interest]

# remove leading '/' if it exists
visit_data_reduced['pagePath_clean'] = [p[1:] if p[0] == '/' else p for p in visit_data_reduced['pagePath_clean']]

# keep only the first part of the remaining page path
visit_data_reduced['pagePath_parent'] = [re.split(r'/| |\?|#', p)[0] for p in visit_data_reduced['pagePath_clean']]
fields_of_interest = ['fullVisitorId', 'visitId', 'hour', 'minute', 'pagePath', 'pagePath_parent']
visit_data_reduced[visit_data_reduced['fullVisitorId'] == 3250250007886851499][fields_of_interest]

# find the child page
fields_of_interest = ['fullVisitorId', 'visitId', 'pagePath_parent', 'pagePath_child']
visit_data_reduced['pagePath_child'] = [re.split(r'/| |\?|#', p)[-1] for p in visit_data_reduced['pagePath_clean']]
visit_data_reduced[visit_data_reduced['fullVisitorId'] == 3250250007886851499][fields_of_interest]

# concat the parent and child
pagePath_abbreviated = []
for parent, child in zip(visit_data_reduced['pagePath_parent'], visit_data_reduced['pagePath_child']):
    if parent != child:
        pagePath_abbreviated.append(parent + '/' + child)
    else:
        pagePath_abbreviated.append(parent)

visit_data_reduced['pagePath_abbreviated'] = pagePath_abbreviated
fields_of_interest = ['fullVisitorId', 'visitId', 'pagePath_abbreviated']
visit_data_reduced[visit_data_reduced['fullVisitorId'] == 3250250007886851499][fields_of_interest]

# search mask, removes about 4%
search_mask = visit_data_reduced['pagePath_parent'].str.contains('search')
visit_data_reduced = visit_data_reduced[~search_mask]
# empty mask, removes 3.4%
empty_mask = visit_data_reduced['pagePath_parent'] == ''
visit_data_reduced = visit_data_reduced[~empty_mask]
# sign in mask, removes 3.8%
sign_in_mask = visit_data_reduced['pagePath'].str.contains('sign-in')
visit_data_reduced = visit_data_reduced[~sign_in_mask]
# login mask, removes 0.2%
login_mask = visit_data_reduced['pagePath'].str.contains('login')
visit_data_reduced = visit_data_reduced[~login_mask]
# log-in mask, removes 3.2%
log_in_mask = visit_data_reduced['pagePath'].str.contains('log-in')
visit_data_reduced = visit_data_reduced[~log_in_mask]
# done mask, removes 1.0%
done_mask = visit_data_reduced['pagePath_parent'] == 'done'
visit_data_reduced = visit_data_reduced[~done_mask]

fields_of_interest = ['fullVisitorId', 'visitId', 'pagePath', 'pagePath_abbreviated']
visit_data_reduced[visit_data_reduced['fullVisitorId'] == 3250250007886851499][fields_of_interest]

# lag1 page mask, removes 12%
visit_data_reduced['pagePath_abbreviated_lag1'] = visit_data_reduced['pagePath_abbreviated'].shift()
page_mask = visit_data_reduced['pagePath_abbreviated'] != visit_data_reduced['pagePath_abbreviated_lag1']
visit_data_reduced = visit_data_reduced[page_mask]
visit_data_reduced.shape
# create a lag of visitor id to ensure that the lag1 page path relates to the same visitor
# this cuts off the first stage of all journeys (as they have no valid lag 1 page path)
# reduces the dataset down by a further 28%
visit_data_reduced['fullVisitorId_lag1'] = visit_data_reduced['fullVisitorId'].shift()
id_mask = visit_data_reduced['fullVisitorId'] == visit_data_reduced['fullVisitorId_lag1']
visit_data_reduced = visit_data_reduced[id_mask]
visit_data_reduced.shape
visit_data_reduced[['pagePath_abbreviated_lag1', 'pagePath_abbreviated']]
pd.DataFrame(visit_data_reduced['pagePath_abbreviated_lag1'].value_counts()).head(10)
pd.DataFrame(visit_data_reduced['pagePath_abbreviated_lag1'].value_counts()).tail(10)

# 34k levels of unique parent pagePath: might make it difficult to use knn, as its sparse
len(visit_data_reduced['pagePath_abbreviated'].unique())

# do a test train split and predict using the max count cat for the prior page to predict the subsequent page
unique_visitorId = visit_data_reduced['fullVisitorId'].unique()
random_df = pd.DataFrame({'fullVisitorId': unique_visitorId,
                          'random_id': np.random.random(len(unique_visitorId))})
visit_data_reduced = visit_data_reduced.merge(random_df, on='fullVisitorId')
threshold_test_train = 0.7
# train data
fields_keep = ['date', 'fullVisitorId', 'visitId', 'hour', 'minute',
               'pagePath_abbreviated', 'pagePath_abbreviated_lag1']
train_data = visit_data_reduced[visit_data_reduced['random_id'] < threshold_test_train][fields_keep]
train_data[train_data['fullVisitorId'] == 3250250007886851499]

# test data
test_data = visit_data_reduced[visit_data_reduced['random_id'] >= threshold_test_train][fields_keep]
test_data.head()

# build a dictionary of dictionaries for predictions
'''
predictions are based on looking up the (pagePath_parent, pagePath_parent_lag1) tuple in the dictionary
built from the train data, and returning the reciprocal rank of the pagePath_parent
'''

pagePath_predictor = {}
pagePath_count = {}
for p_lag1, p in zip(train_data['pagePath_abbreviated_lag1'], train_data['pagePath_abbreviated']):
    pagePath_predictor[(p_lag1, p)] = pagePath_predictor.get((p_lag1, p), 0) + 1
    pagePath_count[p_lag1] = pagePath_count.get(p_lag1, 0) + 1

pagePath_predictor_unflatten = unflatten(pagePath_predictor)


def top_next_URLs(current_URL, population_fraction=0.01):
    '''
    purely for some data exploration - not really necessary
    for the given URL, returns the top next URLs
    requires the calculation of the dictionaries
    - pagePath_predictor_unflatten
    - pagePath_count
    population_fraction at 0.01 works well
    '''
    for k, v in pagePath_predictor_unflatten[current_URL].items():
        if v > population_fraction * pagePath_count[current_URL]:
            print(k, v)


# companies house
top_next_URLs('companies-house')
top_next_URLs('coronavirus')
top_next_URLs('hm-revenue-customs')
top_next_URLs('driving')
top_next_URLs('new-national-restrictions-from-5-november')
top_next_URLs('transition')
top_next_URLs('vehicle-tax')
top_next_URLs('foreign-travel-advice')
top_next_URLs('universal-credit')

# this is the probability for getting the page prediction correct by random sampling
predictions = []
for p_lag1, p in zip(test_data['pagePath_abbreviated_lag1'], test_data['pagePath_abbreviated']):
    if pagePath_predictor.get((p_lag1, p), 0) == 0:
        predictions.append(0)
    else:
        predictions.append(pagePath_predictor.get((p_lag1, p), 0) / pagePath_count.get(p_lag1, 0))

len(predictions)
np.mean(predictions)

# to calculate the rank, we SORT and ENUMERATE the next_URL:count for each of the current_URL
# note that in the code beneath, we are using a nested structure by calling 'unflatten()'
pagePath_predictor_unflatten = unflatten(pagePath_predictor)

pagePath_predictor_unflatten_ranked = {}
for k, v in pagePath_predictor_unflatten.items():
    temp_dict = {key: rank for rank, key in enumerate(sorted(v, key=v.get, reverse=True), 1)}
    pagePath_predictor_unflatten_ranked[k] = temp_dict

pagePath_predictor_ranked = flatten(pagePath_predictor_unflatten_ranked)

# now we just look up the rank using the test data key (p_lag1, p) in the flattened rank dictionary
reciprocal_rank_predictions = []
for p_lag1, p in zip(test_data['pagePath_abbreviated_lag1'], test_data['pagePath_abbreviated']):
    reciprocal_rank_predictions.append(1 / pagePath_predictor_ranked.get((p_lag1, p), 10000))

# this is the mean reciprocal rank of correct predictions
np.mean(reciprocal_rank_predictions)
test_data['reciprocal_rank_predictions'] = reciprocal_rank_predictions
# add some binary flags so we can say if the correct rank was in the top [x] predictions
test_data['top_10'] = [1 if rrp >= 0.1 else 0 for rrp in test_data['reciprocal_rank_predictions']]
test_data['top_5'] = [1 if rrp >= 0.2 else 0 for rrp in test_data['reciprocal_rank_predictions']]
# calculate the expected value of the flag fields
np.mean(test_data['top_10'])
np.mean(test_data['top_5'])
# write results to file
test_data.to_csv(os.path.join(data_dir, 'processed/test_predictions.csv'), header=True, index=False)

# look at the aggregate MRR performance by category - shine a light on the ease of some predictions
pagePath_abbreviated_lag1_test_MRR = (
    test_data
    .groupby('pagePath_abbreviated_lag1')['reciprocal_rank_predictions']
    .mean()
    .sort_values(ascending=False)
    .reset_index(name='mean_reciprocal_rank'))

pagePath_abbreviated_lag1_test_count = (
    test_data
    .groupby('pagePath_abbreviated_lag1')
    .size()
    .sort_values(ascending=False)
    .reset_index(name='count'))

pagePath_abbreviated_lag1_test_summary = (
    pagePath_abbreviated_lag1_test_count
    .merge(pagePath_abbreviated_lag1_test_MRR, on='pagePath_abbreviated_lag1')
    .sort_values('count', ascending=False)
)

pagePath_abbreviated_lag1_test_summary.head()
