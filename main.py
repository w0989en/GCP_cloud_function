import functions_framework
import yfinance as yf
import pandas as pd

def script_str():
    str_ =  ''' 
<!DOCTYPE html>
<html>
  <head>
    <title>神的網站</title>
  </head>
  <body>
    <div style="width: 90%; margin: 0 auto;">
    <p>我的神人~班代</p>
    <div>
      <a href="https://tw.finance.yahoo.com/">代號參考網站: Yahoo Finance</a>
    </div>
    <div>
      <label>新增代號:</label>
      <input type="text" id="add-input" placeholder="2330.TW" />
      <button id="add-button">新增</button>
    </div>
    <div>
      <label>刪除代號:</label>
      <input type="text" id="remove-input" placeholder="2330.TW" />
      <button id="remove-button">刪除</button>
    </div>
    <div id="button-container"></div>
    <br>

    <div id="chart_div" style="width: 100%; height: 500px;"></div>

    <dataframe></dataframe>

  </div>
  </body>
  
  <script>
    // 從 LocalStorage 中讀取 Array
    var storedArray = JSON.parse(localStorage.getItem("myArray")) || [];

    // 創建兩個 input 窗格和相應的按鈕，用於新增和刪除 Array 中的值
    var addInput = document.getElementById("add-input");
    var addButton = document.getElementById("add-button");
    addButton.addEventListener("click", function() {
      storedArray.push(addInput.value);
      localStorage.setItem("myArray", JSON.stringify(storedArray));
      renderButtons();
      document.getElementById('add-input').value = '';
    });

    var removeInput = document.getElementById("remove-input");
    var removeButton = document.getElementById("remove-button");
    removeButton.addEventListener("click", function() {
      var index = storedArray.indexOf(removeInput.value);
      if (index !== -1) {
        storedArray.splice(index, 1);
        localStorage.setItem("myArray", JSON.stringify(storedArray));
        renderButtons();
        document.getElementById('remove-input').value = '';
      }
    });

    // 遍歷 Array，為每個值創建一個按鈕元素
    var buttonContainer = document.getElementById("button-container");
    function renderButtons() {
      buttonContainer.innerHTML = "";
      for (var i = 0; i < storedArray.length; i++) {
        var button = document.createElement("button");
        button.innerHTML = storedArray[i];
        button.onclick = () => window.location.href = 'https://function-stock-og37mhueqa-uc.a.run.app/?stock='+button.innerHTML;
        buttonContainer.appendChild(button);
      }
    }
    renderButtons();

    // 改表格字體顏色
    var cells = document.querySelectorAll('tr td:nth-of-type(2), tr td:nth-of-type(3)');
      for (var i = 0; i < cells.length; i++) {
          var cell = cells[i];
          var value = parseFloat(cell.textContent);
          // 字體顏色
          if (value == 0) {
          cell.style.color = 'black';
          } else if (value > 0) {
          cell.style.color = 'red';
          } else {
          cell.style.color = 'green';
          }
      }

      // 改背表格景色
      var cells = document.querySelectorAll('tr td:nth-of-type(4)');
      for (var i = 0; i < cells.length; i++) {
          var cell = cells[i];
          var value = parseFloat(cell.textContent);
          // 背景顏色
          if (value == 1) {
          cell.style.backgroundColor = '#ffffff'; // 白色
          } else if (value > 1){
          cell.style.backgroundColor = '#ffdfcf'; // 淡紅色
          } else{
          cell.style.backgroundColor = '#e8ffcf'; // 淡綠色
          }
      }
  </script>

  <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
  <script type="text/javascript">
    google.charts.load('current', {'packages':['corechart']});
    google.charts.setOnLoadCallback(drawChart);

    function drawChart() {
      // 取得data
      const table = document.querySelector('.dataframe'); // 選取表格
      const rows = table.rows; // 取得表格中所有的列
      const secondColumnData = []; // 建立空陣列，儲存第二欄的資料
      secondColumnData.push([rows[0].cells[0].innerText, rows[0].cells[1].innerText, rows[0].cells[2].innerText])
      for (let i = 1; i < rows.length; i++) {
        secondColumnData.push([rows[i].cells[0].innerText, parseFloat(rows[i].cells[1].innerText), parseFloat(rows[i].cells[2].innerText)])
      }

      // google charts
      var data = google.visualization.arrayToDataTable(secondColumnData);
      var options = {
        title: '(%)'
      };

      var chart = new google.visualization.AreaChart(document.getElementById('chart_div'));
      chart.draw(data, options);
    }
  </script>
</html>
    '''
    return str_

@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args
    print(request_args)
    
    if request_json and 'stock' in request_json:
        stock = request_json['stock']
    elif request_args and 'stock' in request_args:
        stock = request_args['stock']
    else:
        stock = '^TWII'

    # get stock price
    stock_ticket = yf.Ticker(stock)
    get_stock = stock_ticket.history(period="1y")
    get_stock[f'{stock}_diff'] = get_stock['Close'].diff()
    get_stock[f'{stock}_%'] = 100 * get_stock[f'{stock}_diff'] / get_stock['Close']
    get_stock = get_stock.iloc[::-1]

    # get TWII
    stock_ticket = yf.Ticker("^TWII")
    get_twii = stock_ticket.history(period="1y")
    get_twii['TWII_diff'] = get_twii['Close'].diff()
    get_twii['TWII_%'] = 100 * get_twii['TWII_diff'] / get_twii['Close']
    get_twii = get_twii.iloc[::-1]

    # merge data
    fin = pd.concat([get_twii['TWII_%'], get_stock[f'{stock}_%']], axis=1)
    fin['RS'] = fin[f'{stock}_%'] / fin['TWII_%']
    fin = fin.round(3)
    fin = fin[0:len(fin)-1]
    fin['date'] = [x.strftime(" %Y-%m-%d ") for x in fin.index.to_pydatetime()]
    fin = fin[['date', 'TWII_%', f'{stock}_%', 'RS']]
    fin_table = fin.to_html(index=False)
    
    return_html = script_str().replace('<dataframe></dataframe>', fin_table)
    return return_html
