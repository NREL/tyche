exec(open("src/waterfall/setup.py").read())

print("\nSaving optimum.amounts:")
setup_amounts = optimum.amounts.copy()
print(setup_amounts)


from itertools import permutations

class Waterfall:
  """
  amounts : DataFrame
  order : array
  evaluator : Evaluator
  raw : DataFrame
  max_amount : float
  path : string
  values : array of DataFrames
  """
  def __init__(self,
    amounts,
    evaluator,
    order = None,
    metric = None,
    max_amount = None,
    data = os.path.abspath(os.path.join("src","waterfall","data"))
  ):
    print("\nCreate waterfall for the following investments\n", amounts, "\n")
    self._data_path = data

    self.evaluator = evaluator
    self.amounts = pd.DataFrame(amounts.copy())
    
    if type(max_amount)==float: self.max_amount = max_amount
    else:                       self.max_amount = self.total_amount()

    raw = evaluator.raw.copy().reset_index()
    raw = raw[['Category','Index','Units','Technology']].drop_duplicates()
    raw['Metric'] = metric
    self.raw = raw.set_index(['Category','Index'])

    # Set properties: order, path, and values.
    self.order = order
    self.refresh(order)
    return None


  def refresh(self, order):
    """
    Update Waterfall parameters: order, path, and values for the given order.

    Parameters
    ----------
    order : np.ndarray
      Investment order
    """
    order = self._order(order)
    self._path()
    self.values = []
    return order


  def total_amount(self):
    """
    Return the total amount invested.
    """
    return self.amounts.sum().values[0].round()


  def metric(self):
    """
    Return the metric for which the original optimization was performed.
    """
    return self.raw['Metric'].unique()


  def technology(self):
    """
    Return the technology/ies for which the solution is optimal.
    """
    return self.raw['Technology'].unique()


  def sample_count(self):
    """
    Return the number of samples used in the model.
    """
    return self.evaluator.interpolators.reset_index()['Sample'].max()


  def evaluate_investments(self, order):
    """
    Parameters
    ----------
    order : array
      order in which to invest in categories
    """
    amounts = self._select_loc(self.amounts.copy(), order)
    value = self.evaluator.evaluate(amounts)

    # Before saving, join input options to 'values' and amounts to use for plot annotation.
    value = pd.DataFrame(value)
    value = value.join(self.raw, on=self.raw.index.names)
    value = value.join(amounts, on=amounts.index.names)

    self.values.append(value)
    self.values[-1].to_csv(self._save_as("value", order=order))
    return self


  def cascade_investments(self, order=None):
    """
    Iteratively invest in each category in the order given,
    saving the results after each investment.

    Parameters
    ----------
    order : array
    """
    order = self.refresh(order)
    print("Cascading investment order: ", order+1)

    [self.evaluate_investments(order[:ii]) for ii in np.arange(0,len(order)+1)]

    # Save amounts and order -- !!!! How much do we care about saving max amount?
    amounts = self.amounts.copy()
    amounts['Maximum'] = self.max_amount
    amounts.to_csv(self._save_as('amounts'))
    
    pd.DataFrame({'Order' : order+1}).to_csv(self._save_as('order'), index=False)

    return self.values


  def cascade_permutations(self):
    """
    Invest in all permutations of investment order.
    """
    N = len(self.evaluator.categories)
    orders = [np.array(order) for order in permutations(np.arange(0,N), N)]

    [self.cascade_investments(order=order) for order in orders]
    print("Results saved to\n", os.path.join(self._data_path, str(self._uuid())))
    return self


  def _select_loc(self, df, idx):
    """
    Invest in *only* the given indices. Set all other amounts to zero.

    Parameters
    ----------
    df : DataFrame
      Investment amounts
    idx : array
      Integer indices
    """
    return self._zero_value(df, np.setdiff1d(np.arange(0,len(df)), idx))


  def _zero_value(self, df, idx, column='Amount'):
    """
    Set investment amounts to zero.

    Parameters
    ----------
    df : DataFrame
      Investment amounts
    idx : array
      Integer indices
    column : 'Amount'
      name of column of values to set to zero
    """
    index_names = df.index.names
    df = df.reset_index()
    df.loc[idx,column] = 0
    return df.set_index(index_names)


  def _order(self, order=None):
    """
    Set and return invsestment order as an array. If no input order is given,
    initialize to 0:N-1, where N is the number of investment categories.

    Parameters
    ----------
    order : array
      Investment order
    """
    if type(order)==list:       order=np.array(order)
    # If no input order is given and Waterfall order is already defined, use that.
    # If order has not yet been defined, set it as 0:N-1, where N is the number of
    # investment categories.
    if type(order)!=np.ndarray:
      if self.order==np.ndarray: order=self.order
      else:                      order=np.arange(0, len(self.evaluator.categories))
    if 0 not in order:           order-=1

    self.order = order
    return order


  def _path(self):
    """
    Return the path to the directory to which waterfall cascade data will be saved.
    If necessary, make this path.
    """
    # Add UUID to the path and create directory, if necessary.
    path = os.path.join(self._data_path, str(self._uuid()))
    if not os.path.isdir(path): os.mkdir(path)

    # Add INVESTMENT ORDER to the path and create directory, if necessary.
    path = os.path.join(path, self._print_order())
    if not os.path.isdir(path): os.mkdir(path)
    
    self.path = path
    return self.path


  def _save_as(self, name, order=None, ext=".csv"):
    """
    Return the path to the file to which data will be saved. If `order=None`, this will be
    formatted: `<Waterfall.path>/name.csv`. If `order` are given, this will be
    formatted: `<Waterfall.path>/name_num-order.csv`, where
    `num` is the total number of investments that have been made so far, and
    `order` shows the investment order, with all investments that have not yet been
    made set to zero.

    Parameters
    ----------
    name : string
      descriptor of type of information (e.x., amounts, values)
    order : array
      order in which to invest in categories
    ext : string
      file extension (default: '.csv')
    """
    if type(order)==np.ndarray:
      # Number of investments:
      ii = str(len(self.values)-1)
      # Indices of investments made (0 for null investment)
      order = '-'.join([ii, self._print_order(order)])
      name = '_'.join([name,order])
    return os.path.join(self.path, name+ext)


  def _uuid(self):
    """
    Return a UUID based on optimizer input options:
    - Metric
    - Technology
    - Sample count
    - Total amount
    - Amount
    """
    lst = [
      *self.metric(),
      *self.technology(),
      self.sample_count(),
      self.total_amount(),
      *self.amounts['Amount'].values.round(),
    ]
    uuid_str = ' '.join([str(x) for x in lst if x!=None])
    return uuid.uuid3(uuid.NAMESPACE_DNS, uuid_str)
  

  def _print_order(self, lst=None):
    """
    Return a string of integers defining the order in which investments were made.
    """
    if type(lst)!=np.ndarray: lst=self.order
    string = ''.join([str(x) for x in lst+1])
    return string.ljust(len(self.order), '0')


# ------------------------------------------------------------------------------------------
# exec(open("src/waterfall/Waterfall.py").read())

w = Waterfall(
  optimum.amounts.copy(),
  evaluator,
  metric = args['target_metric'],
  max_amount = args['max_amount'],
)

w.cascade_permutations()