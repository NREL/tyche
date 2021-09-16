class Waterfall:
  """
  amounts : DataFrame
  evaluator : Evaluator
  order : array
  """
  def __init__(self,
    optimum,
    evaluator,
    order,
    metric = None,
    data = os.path.abspath(os.path.join("src","waterfall","data"))
  ):
    self._sample_count = evaluator.interpolators.reset_index()['Sample'].max()
    self._technology = evaluator.raw.reset_index()['Technology'].unique()
    self._total_amount = optimum.amounts.sum().round()
    self._metric = metric

    if type(order)==list: order=np.array(order)
    if 0 not in order:  order-=1
    self.order = order

    # After all other parameters have been defined, can define path
    self.path = data

    # Save investment information.
    self.amounts = pd.DataFrame(optimum.amounts).copy()

    # Get notes.
    raw = evaluator.raw.copy().reset_index()
    raw = raw[['Category','Index','Units','Technology']].drop_duplicates()
    raw['Metric'] = metric
    self.raw = raw.set_index(['Category','Index'])

    self.evaluator = evaluator
    self.values = []


  def evaluate_investments(self, investments):
    print(investments,"\t",len(investments))
    amounts = self._select_loc(self.amounts, investments)
    value = self.evaluator.evaluate(amounts)

    # Join input options to 'values' and amounts before saving
    # to use for plot annotation.
    value = pd.DataFrame(value)
    value = value.join(self.raw, on=self.raw.index.names)
    value = value.join(amounts, on=amounts.index.names)

    self.values.append(value)
    self.values[-1].to_csv(self._save_as("value", investments=investments))
    return self

  def cascade_investments(self):
    path = os.path.join(self.path, str(self._uuid()))
    if not os.path.isdir(path): os.mkdir(path)
    self.path = path

    order = self.order
    N = len(order)

    [self.evaluate_investments(order[:ii]) for ii in np.arange(0,N+1)]
    return self.values


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

  def _save_as(self, name, investments=None, ext=".csv"):
    """
    Path to file to which data will be saved. If `investments=None`, this will be
    formatted: `<Waterfall.path>/name.csv`. If `investments` are given, this will be
    formatted: `<Waterfall.path>/name_num-investments.csv`, where
    `num` is the total number of investments that have been made so far, and
    `investments` shows the investment order with all investments that have not yet been
    made set to zero.
    """
    if type(investments)==np.ndarray:
      print(name,"\n")
      # Number of investments:
      ii = str(len(self.values)-1)
      # Indices of investments made (0 for null investment)
      investments = ''.join([str(x) for x in investments+1])
      investments = investments.ljust(len(w.order), '0')
      investments = '-'.join([ii,investments])
      name = '_'.join([name,investments])
      
    return os.path.join(self.path, name+ext)

  def _uuid(self):
    """
    Generate a UUID based on the following input options (if given):
    - Target metric
    - Technology
    - 
    """
    lst = [
      self._metric,
      *self._technology,
      self._sample_count,
      self._total_amount,
      *self.order,
    ]
    uuid_str = ' '.join([str(x) for x in lst if x!=None])
    return uuid.uuid3(uuid.NAMESPACE_DNS, uuid_str)


# ------------------------------------------------------------------------------------------

exec(open("src/waterfall/setup.py").read())

w = Waterfall(
  optimum,
  evaluator,
  args['Order'],
  metric = args['target_metric'],
)

w.cascade_investments()