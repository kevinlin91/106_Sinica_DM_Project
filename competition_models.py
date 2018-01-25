import graphviz
import pydotplus

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

from sklearn import linear_model,svm,tree,ensemble
from sklearn.model_selection import cross_val_score
from sklearn.externals.six import StringIO
from IPython.display import Image

from competition_preprocessing import compPreProcessor

def linear_regression_sm(competitions):
    results = smf.ols('Top10 ~ DataSizeBytes + RewardQuantity + Duration + ParallelCompetitions', data=competitions).fit()
    print(results.summary())
    
def linear_regression(features, target):
    lr = linear_model.LinearRegression()
    print("Running linear regression with the following parameters:")
    print(lr)
    lr.fit(features, target)
    print_metrics(lr, features, target)
    print_coefficients(lr, features)

def logistic_regression_sm(features, target):
    logit = sm.Logit(target, features)
    results = logit.fit()

    # Library Bug workaround
    from scipy import stats
    stats.chisqprob = lambda chisq, df: stats.chi2.sf(chisq, df)

    print(results.summary())

def logistic_regression(features, target):
    lr = linear_model.LogisticRegression(fit_intercept=False, C=1e9) # no intercept to make consistent with sm
    print("Running logistic regression with the following parameters:")
    print(lr)
    lr.fit(features, target)
    print_metrics(lr, features, target)
    print_coefficients(lr, features)

def support_vector_regression(features, target, kernel='linear'):
    svr = svm.SVR(kernel=kernel)
    print("Running support vector regression with the following parameters:")
    print(svr)
    svr.fit(features, target)
    print_metrics(svr, features, target)
    print_coefficients(svr, features)

def decision_tree_regression(features, target):
    dt = tree.DecisionTreeRegressor(max_depth=3, max_features='sqrt')
    print("Running regression tree with the following parameters:")
    print(dt)
    dt.fit(features, target)
    print_metrics(dt, features, target)
    print_feat_importance(dt, features)
    return dt

def decision_tree_classification(features, target):
    dt = tree.DecisionTreeClassifier(max_depth=3, max_features='sqrt')
    print("Running decision tree classificaiton with the following parameters:")
    print(dt)
    dt.fit(features, target)
    print_metrics(dt, features, target)
    print_feat_importance(dt, features)
    return dt

def plot_tree(model, features, filepath = './output/decision_tree'):
    dot_data = StringIO()
    dot_data = tree.export_graphviz(dt, out_file=None, precision=1,
                    filled=True, rounded=True, feature_names = features, proportion=True,
                    special_characters=True)

    graph = graphviz.Source(dot_data)
    graph.render(filepath)
    print("Tree available in "+filepath+".pdf")

def random_forest_regression(features, target):
    forest = ensemble.RandomForestRegressor(max_depth=4, min_samples_leaf=5, random_state=0)
    print("Running random forest regression with the following parameters:")
    print(forest)
    forest.fit(features, target)
    print_metrics(forest, features, target)
    print_feat_importance(forest, features)

def random_forest_classification(features, target):
    forest = ensemble.RandomForestClassifier(max_depth=4, min_samples_leaf=5, random_state=0)
    print("Running random forest classification with the following parameters:")
    forest.fit(features, target)
    print_metrics(forest, features, target)
    print_feat_importance(forest, features)

def print_feat_importance(model, features):
    fs = sorted(zip(map(lambda x: round(x, 3), model.feature_importances_), features), reverse=True)
    print("{:<25} {:}".format('Feature','Importance'))
    print("{:<25} {:}".format('---------------------','----------'))
    for value, feature in fs:
        print("{:<25} {:.2f}".format(feature, value))
    print("\n")

def print_metrics(model, features, target):
    print("\nExplained Variance (R2):" , model.score(features, target),)
    cv_score = cross_val_score(model, features, target, cv=10).mean()
    print("Cross validated score (R2):", cv_score, "\n")

def print_coefficients(model, features):
    coef = model.coef_
    if coef.shape[0] != len(features.columns):
        coef = coef[0]
    fs = sorted(zip(map(lambda x: round(x, 3), coef), features), reverse=True)
    print("{:<25} {:}".format('Feature','Coefficient'))
    print("{:<25} {:}".format('---------------------','----------'))
    for value, feature in fs:
        print("{:<25} {:.2f}".format(feature, value))
    print("\n")

if __name__ == '__main__':
    competitions = compPreProcessor().get_competitions()

    # Subset competitions
    competitions = competitions.loc[competitions.USD == 1]
    # print(competitions.describe())

    # Select Features and Target target
    features = competitions[['RewardQuantity', 'DataSizeBytes', 'Duration', 'ParallelCompetitions']]
    target = competitions['Top10']

    #
    # Regressions
    #
    linear_regression_sm(competitions) # Calculates significance levels
    linear_regression(features, target)

    dt = decision_tree_regression(features, target)
    plot_tree(dt, features.columns.values, 'output/regression_tree')

    random_forest_regression(features, target)

    #
    # Classifications
    # 
    target = target > 10 # Binary target label
    print(sum(target)/len(competitions.Top10))

    logistic_regression_sm(features, target)
    logistic_regression(features, target)

    random_forest_classification(features, target)

    dt = decision_tree_classification(features, target)
    plot_tree(dt, features.columns.values)

