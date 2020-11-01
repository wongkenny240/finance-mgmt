"""
Author: KCKW
Description: fetch account information from IBKR Flex Web Service
"""

from ibflex import client
import lxml.objectify as lxml_objectify
import numpy as np
import pandas as pd


class FlexStatement(object):

    def __init__(self, path, switch):
        self.path = path

        # This is a large object, so I let it be garbage-collected
        stmt = self.get_lxml_root()

        '''
        self.perf = clean_perf(stmt)
        self.option_perf = clean_option_perf(self.perf)

        self.option_perf_underlying = rollup_option_underlying(
            self.option_perf)

        self.stock_perf = clean_stock_perf(self.perf)
        
        '''
        if switch == 'position':
            self.position = clean_position(stmt)
        elif switch == 'dividend':
            self.cash_transactions = clean_cash(stmt)
            self.dividends = clean_dividends(self.cash_transactions)
            self.dividends_by_symbol = (self.dividends.groupby('symbol').amount.sum())

            self.cash_by_type = self.cash_transactions.groupby('type').amount.sum()
            self.fees = clean_fees(self.cash_transactions)

            self.in_out = clean_in_out(self.cash_transactions)

        elif switch == 'commission':
            self.commission = clean_commission(stmt)
        elif switch == 'trade':
            self.trade = clean_trade(stmt)

    def get_lxml_root(self):
        tree = lxml_objectify.parse(open(self.path, 'rb'))
        root = tree.getroot()
        return root.FlexStatements.FlexStatement


'''
def clean_perf(statement):
    summary = statement.MTDYTDPerformanceSummary
    perf = get_table(summary)

    numeric_cols = ['mtmYTD', 'mtmMTD', 'realSTMTD', 'realSTYTD',
                    'realLTMTD', 'realLTYTD']

    for c in numeric_cols:
        perf[c] = perf[c].astype(np.float64)
    return perf

'''


def get_table(node):
    return pd.DataFrame([dict(zip(c.keys(), c.values())) for
                         c in node.getchildren()])


def clean_position(stmt):
    return


def clean_commission(statement):
    commission = get_table(statement.UnbundledCommissionDetails)
    commission['dateTime'] = pd.to_datetime(commission['dateTime'])
    return commission[['description', 'dateTime', 'totalCommission']]


def clean_fees(cash_trans):
    fees = cash_trans.loc[(cash_trans.type == 'Broker Interest Paid') | (cash_trans.type == 'Broker Interest Received') | (cash_trans.type == 'Other Fees') ,:]
    fees['amount'] = pd.to_numeric(fees['amount'])
    return fees


def clean_option_perf(perf):
    perf = perf[perf.assetCategory == 'OPT'].copy()
    perf['expiry'] = pd.to_datetime(perf['expiry'])
    return perf


def clean_stock_perf(perf):
    perf = perf[perf.assetCategory == 'STK']

    perf = perf.drop(['acctAlias',
                      'assetCategory',
                      'expiry',
                      'multiplier',
                      'putCall',
                      'strike',
                      'securityID',
                      'securityIDType',
                      'underlyingSymbol',
                      'underlyingConid'], axis='columns')
    return perf.set_index('symbol')


def rollup_option_underlying(options):
    grouped = options.groupby('underlyingSymbol')

    return pd.DataFrame({
        'mtmYTD': grouped.mtmYTD.sum(),
        'realSTYTD': grouped.realSTYTD.sum(),
        'realLTYTD': grouped.realLTYTD.sum(),
    })


def rollup_statements(statements, key='mtm_ytd'):
    def clean(x):
        return x.drop('Total', axis=1)

    result = clean(getattr(statements[0], key))
    for stmt in statements[1:]:
        result = result.add(clean(getattr(stmt, key)),
                            fill_value=0)

    result = result.fillna(0)
    result['Total'] = result.sum(1)

    return result


def clean_cash(statement):
    cash_trans = get_table(statement.CashTransactions)
    cash_trans.amount = cash_trans.amount.astype(np.float64)
    cash_trans.dateTime = pd.to_datetime(cash_trans.dateTime)
    return cash_trans


def clean_dividends(cash_trans):
    dividends = cash_trans[cash_trans.type.str.contains('Dividends')]

    return dividends[['accountId',  # 'assetCategory', 'underlyingSymbol',
                      'symbol', 'dateTime', 'description',
                      'amount']]


def clean_trade(statement):
    trade = get_table(statement.Trades)
    trade.cost = trade.cost.astype(np.float64)
    trade.dateTime = pd.to_datetime(trade.dateTime)
    return trade[['symbol', 'description', 'dateTime', 'quantity', 'tradePrice', 'ibCommission', 'netCash', 'cost']]


def total_fees(cash_trans):
    total_by_type = cash_trans.groupby('type').amount.sum()

    return total_by_type[['Broker Interest Paid',
                          'Broker Interest Received',
                          'Other Fees']]


def clean_in_out(cash_trans):
    inout = cash_trans[cash_trans.type == 'Deposits & Withdrawals']

    return pd.Series([inout.amount[inout.amount > 0].sum(),
                      inout.amount[inout.amount < 0].sum()],
                     index=['Deposit', 'Withdrawal'])

def save_df(df, path):
    df.to_csv(path, index=False)
    return


if __name__ == '__main__':
    query_id_list = 'YOUR DICT'
    token = 'YOUR TOKEN'

    for tbl, query_id in query_id_list.items():
        response = client.download(token, query_id)
        print(response)
        filename = tbl + '.xml'
        report_file = open(filename, 'wb')
        report_file.write(response)
        report_file.close()

    statements = FlexStatement('trade.xml', 'trade')
    trade = statements.trade
    print(trade)

    statements = FlexStatement('dividend.xml', 'dividend')
    fees = statements.fees
    print(fees)

    dividends = statements.dividends
    print(dividends)
    dividends_by_symbol = statements.dividends_by_symbol
    print(dividends_by_symbol)
