```javascript
// This file is required by the index.html file and will
// be executed in the renderer process for that window.
// No Node.js APIs are available in this process because
// `nodeIntegration` is turned off. Use `preload.js` to
// selectively enable features needed in the rendering
// process.
const { remote, shell, ipcRenderer, desktopCapturer } = require('electron')
const TabGroup = require("electron-tabs");
const fs = require('fs');
const path = require("path");
// const { thriftClient } = require('./boardmgr');

window.$ = window.jQuery = require("jquery");
require('../../node_modules/bootstrap/dist/js/bootstrap.min.js');

log = remote.getGlobal('logsrv').scope('index')

var logexport_btn = document.querySelector('#logexport_btn')
var logparser_btn = document.querySelector('#logparser_btn')
var trace_btn = document.querySelector('#gettrace_btn')
var cycleview_btn = document.querySelector('#cycleview_btn')
var boardmgr_btn = document.querySelector('#boardmgr_btn')
var ddrconfig_btn = document.querySelector('#ddrconfig_btn')
var sysview_btn = document.querySelector('#sysview_btn')
var ddrscan_btn = document.querySelector('#ddrscan_btn')
var bus_monitor_btn = document.querySelector('#bus_monitor_btn')
var feedback_btn = document.querySelector('#feedback_btn')
var setting_btn = document.querySelector('#setting_btn')


const index_id = remote.getCurrentWebContents().id;
log.info("index_id");
log.info(index_id);


const showDiv = document.getElementById('showDiv');
function get_xy() {
  var posX = 0, posY = 0;
  var event = event || window.event;
  if (event.pageX || event.pageY) {
      posX = event.pageX;
      posY = event.pageY;
  } else if (event.clientX || event.clientY) {
      posX = event.clientX + document.documentElement.scrollLeft + document.body.scrollLeft;
      posY = event.clientY + document.documentElement.scrollTop + document.body.scrollTop;
  }
  // log.info(posX)
  // log.info(posY)
  showDiv.style.left = posX.toString() + 'px';
  showDiv.style.top = posY.toString() + 'px';
  showDiv.style.display = 'block';

  return [posX, posY];
}

function set_showdiv(posX, posY, content) {
  showDiv.style.left = posX.toString() + 'px';
  showDiv.style.top = posY.toString() + 'px';
  showDiv.style.display = 'block';

  showDiv.innerHTML = content;
}

function disappear_showdiv() {
  showDiv.style.display = 'none';
}

logexport_btn.onmouseover = function () {
  var posX, posY;
  [posX, posY] = get_xy();
  set_showdiv(posX, posY+10, "日志导出");
}

logexport_btn.onmouseout = function () {
  disappear_showdiv();
}

logparser_btn.onmouseover = function () {
  var posX, posY;
  [posX, posY] = get_xy();
  set_showdiv(posX, posY+10, "日志解析");
}

logparser_btn.onmouseout = function () {
  disappear_showdiv();
}

trace_btn.onmouseover = function () {
  var posX, posY;
  [posX, posY] = get_xy();
  set_showdiv(posX, posY+10, "trace工具");
}

trace_btn.onmouseout = function () {
  disappear_showdiv();
}

cycleview_btn.onmouseover = function () {
  var posX, posY;
  [posX, posY] = get_xy();
  set_showdiv(posX, posY+10, "CycleView");
}

cycleview_btn.onmouseout = function () {
  disappear_showdiv();
}

boardmgr_btn.onmouseover = function () {
  var posX, posY;
  [posX, posY] = get_xy();
  set_showdiv(posX, posY+10, "单板管理");
}

boardmgr_btn.onmouseout = function () {
  disappear_showdiv();
}

ddrconfig_btn.onmouseover = function () {
  var posX, posY;
  [posX, posY] = get_xy();
  set_showdiv(posX, posY+10, "xloader配置工具");
}

ddrconfig_btn.onmouseout = function () {
  disappear_showdiv();
}
sysview_btn.onmouseover = function () {
  var posX, posY;
  [posX, posY] = get_xy();
  set_showdiv(posX, posY+10, "sysview");
}

sysview_btn.onmouseout = function () {
  disappear_showdiv();
}

ddrscan_btn.onmouseover = function () {
  var posX, posY;
  [posX, posY] = get_xy();
  set_showdiv(posX, posY+10, "DDR测试");
}

ddrscan_btn.onmouseout = function () {
  disappear_showdiv();
}

bus_monitor_btn.onmouseover = function () {
  var posX, posY;
  [posX, posY] = get_xy();
  set_showdiv(posX, posY+10, "bus_monitor");
}

bus_monitor_btn.onmouseout = function () {
  disappear_showdiv();
}

feedback_btn.onmouseover = function () {
  var posX, posY;
  [posX, posY] = get_xy();
  set_showdiv(posX, posY+10, "反馈");
}

feedback_btn.onmouseout = function () {
  disappear_showdiv();
}

setting_btn.onmouseover = function () {
  var posX, posY;
  [posX, posY] = get_xy();
  set_showdiv(posX, posY+10, "设置");
}

setting_btn.onmouseout = function () {
  disappear_showdiv();
}

var tabGroup = new TabGroup({
  // newTab: {
  //   title: 'New Tab'
  // }
});

// tabGroup.on("tab-active", (tab, tabGroup) => {
//   let active_tab = tabGroup.getActiveTab();
//   let webid = active_tab.id+3
//   log.info("tab-active" + webid)
//   ipcRenderer.sendTo(webid, "change_session", webid)
// });

function show_index() {
  let welcometab = tabGroup.addTab({
    title: "欢迎使用",
    src: "core/html/welcome.html",
    visible: true,
    active: true,
    webviewAttributes: { sourceMap: true, javaScriptEnabled: true, nodeIntegration: true }
  });
}
show_index()

var logexporttabid = 0;
var logexporttab = null
logexport_btn.onclick = function () {
  log.info("logexport clicked");
  //document.getElementById("logexport_btn").value = "test0";
  //document.getElementById("subapp_frame").src = "apps/logexport/demo_iframe.html";
  if (logexporttabid == 0) {
    logexporttab = tabGroup.addTab({
      title: '日志导出',
      src: 'apps/logexport/src/logexport.html',
      visible: true,
      active: true,
      webviewAttributes: { sourceMap: true, javaScriptEnabled: true, nodeIntegration: true, WebContentsDebuggingEnabled: true }
    });
    logexporttab.webview.addEventListener('did-stop-loading', (event) => {
      log.info('logexporttab finishload')
      logexporttabid = logexporttab.webview.getWebContentsId();
      log.info("logexporttabid " + logexporttabid);
      log.info("tab webcontentsid " + logexporttab.id);
      // const export_msg = document.querySelector('#export_msg');
      // ipcRenderer.on('logexport', (e, data) => {
      //   log.info("logexport:"+ data);
      //   export_msg.textContent = data;
      // })
    });

    logexporttab.on("close", (logexporttab) => {
      log.info("logexporttab close.");
      logexporttabid = 0;
    });
    // log.info("logexporttabid is " + logexporttab.id)
  } else {
    tabGroup.getTab(logexporttab.id).activate();
    log.info("back-logexporttabid " + logexporttabid);
  }
}


// var logparsertab = null
logparser_btn.onclick = function () {
  log.info("logparser clicked");
  let logparsertab = tabGroup.addTab({
    title: "日志解析",
    src: "apps/logparser/src/logparser.html",
    visible: true,
    active: true,
    webviewAttributes: { sourceMap: true, javaScriptEnabled: true, nodeIntegration: true }
  });
  logparsertab.webview.addEventListener('did-finish-load', (event) => {
    log.info('logparsertab finishload1')
    let logparsertabid = logparsertab.webview.getWebContentsId();
    log.info("tab webcontentsid " + logparsertabid);
    // ipcRenderer.sendTo(logparsertabid, "get_current_id", logparsertabid)
    logparsertab.on("active", (tab) => {
      log.info('logparsertab load')
      // let logparsertabid = logparsertab.webview.getWebContentsId();
      log.info("tab webcontentsid " + logparsertabid);
      ipcRenderer.sendTo(logparsertabid, "change_session", logparsertabid);
    });
  })
  // log.info("logparsertabid is " + logparsertab.id)


}

var tracetabid = 0
var tracetab = null
trace_btn.onclick = function () {
  log.info("trace clicked");
  if (tracetabid == 0) {
    tracetab = tabGroup.addTab({
      title: 'trace',
      src: 'apps/gettrace/src/gettrace.html',
      visible: true,
      active: true,
      webviewAttributes: { sourceMap: true, javaScriptEnabled: true, nodeIntegration: true, WebContentsDebuggingEnabled: true }
    });
    tracetab.webview.addEventListener('did-finish-load', (event) => {
      log.info('tracetab finishload')
      tracetabid = tracetab.webview.getWebContentsId();
      log.info("tracetabid " + tracetabid);
      log.info("tab webcontentsid " + tracetab.id);
    });

    tracetab.on("close", (tracetab) => {
      log.info("tracetab close.");
      tracetabid = 0;
    });
  } else {
    tabGroup.getTab(tracetab.id).activate();
    log.info("back-tracetabid " + tracetabid);
  }
}

var cycleviewtab = null
cycleview_btn.onclick = function () {
  log.info("cycleview_btn clicked");
  //document.getElementById("cycleview_btn").value = "test1";
  //document.getElementById("subapp_frame").src = "apps/cycleview/demo_iframe.html";
  cycleviewtab = tabGroup.addTab({
    title: "Cycle view",
    src: "apps/cycleview/src/treetable-lay/demo/index.html",
    visible: true,
    active: true,
    webviewAttributes: { sourceMap: true, javaScriptEnabled: true, nodeIntegration: true }
  });
}


boardmgr_btn.onclick = function () {
  log.info("boardmgr clicked");
}

ddrconfig_btn.onclick = function () {
  log.info("ddrconfig_btn clicked");
  //document.getElementById("logparse_btn").value = "test1";
  //document.getElementById("subapp_frame").src = "apps/logparser/demo_iframe.html";
  tabGroup.addTab({
    title: "xloader配置工具",
    src: "apps/ddrconfig/src/ddrconfig.html",
    visible: true,
    active: true,
    webviewAttributes: { sourceMap: true, javaScriptEnabled: true, nodeIntegration: true }
  });
}
var sysviewtabid = 0
var sysviewtab = null
sysview_btn.onclick = function () {
  log.info("sysview_btn clicked");
  if (sysviewtabid == 0) {
    sysviewtab = tabGroup.addTab({
      title: 'sysview',
      src: 'apps/sysview/src/sysview.html',
      visible: true,
      active: true,
      webviewAttributes: { sourceMap: true, javaScriptEnabled: true, nodeIntegration: true, WebContentsDebuggingEnabled: true }
    });
    sysviewtab.webview.addEventListener('did-finish-load', (event) => {
      log.info('sysviewtab finishload')
      sysviewtabid = sysviewtab.webview.getWebContentsId();
      log.info("sysviewtabid " + sysviewtabid);
      log.info("tab webcontentsid " + sysviewtab.id);
    });

    sysviewtab.on("close", (sysviewtab) => {
      log.info("sysviewtab close.");
      sysviewtabid = 0;
    });
  } else {
    tabGroup.getTab(sysviewtab.id).activate();
    log.info("back-sysviewtabid " + sysviewtabid);
  }
}

var ddrscantabid = 0
var ddrscantab = null
ddrscan_btn.onclick = function () {
  log.info("ddrscan clicked");
  //document.getElementById("logparse_btn").value = "test1";
  //document.getElementById("subapp_frame").src = "apps/logparser/demo_iframe.html";
  if (ddrscantabid == 0) {
  ddrscantab = tabGroup.addTab({
    title: "DDR测试",
    src: "apps/ddrscan/src/ddrscan.html",
    visible: true,
    active: true,
    webviewAttributes : { sourceMap: true, javaScriptEnabled: true, nodeIntegration: true, WebContentsDebuggingEnabled: true }
  });
    ddrscantab.webview.addEventListener('did-finish-load', (event) => {
      log.info('ddrscantab finishload')
      ddrscantabid = ddrscantab.webview.getWebContentsId();
      log.info("ddrscantabid " + ddrscantabid);
      log.info("tab webcontentsid " + ddrscantab.id);
    });

    ddrscantab.on("close", (ddrscantab) => {
      log.info("ddrscantab close.");
      ddrscantabid = 0;
    });
  } else {
    tabGroup.getTab(ddrscantab.id).activate();
    log.info("back-ddrscantabid " + ddrscantabid);
  }
}

var bus_monitortabid = 0
var bus_monitortab = null
bus_monitor_btn.onclick = function () {
  log.info("bus_monitor_btn clicked");
  if (bus_monitortabid == 0) {
    bus_monitortab = tabGroup.addTab({
      title: 'bus_monitor',
      src: 'apps/bus_monitor/src/bus_monitor.html',
      visible: true,
      active: true,
      webviewAttributes: { sourceMap: true, javaScriptEnabled: true, nodeIntegration: true, WebContentsDebuggingEnabled: true }
    });
    bus_monitortab.webview.addEventListener('did-finish-load', (event) => {
      log.info('bus_monitortab finishload')
      bus_monitortabid = bus_monitortab.webview.getWebContentsId();
      log.info("bus_monitortabid " + bus_monitortabid);
      log.info("tab webcontentsid " + bus_monitortab.id);
    });

    bus_monitortab.on("close", (bus_monitortab) => {
      log.info("bus_monitortab close.");
      bus_monitortabid = 0;
    });
  } else {
    tabGroup.getTab(bus_monitortab.id).activate();
    log.info("back-bus_monitortabid " + bus_monitortabid);
  }
}

function feedback_action() {
  shell.openExternal('http://rnd-bdp.huawei.com/ng2/mts')
}


function determineScreenShotSize () {
  const screenSize = remote.screen.getPrimaryDisplay().workAreaSize
  const maxDimension = Math.max(screenSize.width, screenSize.height)
  return {
    width: maxDimension * window.devicePixelRatio,
    height: maxDimension * window.devicePixelRatio
  }
}

const syslog_path = remote.getGlobal('LOG_PATH')
async function getScreenStream() {
  // var screenSize = remote.screen.getPrimaryDisplay().workAreaSize
  var screenSize = determineScreenShotSize()
  log.info(screenSize);
  let option = { types: ['screen'], thumbnailSize: screenSize }
  // const sources = await desktopCapturer.getSources({ types: ['screen'], });
  const sources = await desktopCapturer.getSources(option);
  log.info(sources);
  var screen_filepath = []
  for (const source of sources) {
    // log.info(source.thumbnail.toDataURL());
    // screen_srcs.push(source.thumbnail.toDataURL());
    // save_sys_screenshot()
    let screenfile = path.join(syslog_path, source.name + '.png')
    // log.info(screenfile)
    fs.writeFile(screenfile, source.thumbnail.toPNG(), () => {
      log.info("save sys screenshot ok.")
    })
    screen_filepath.push(screenfile);
  }
  // log.info(screen_srcs)
  return screen_filepath;
}


function feedback() {
  log.info("feedback clicked");

  getScreenStream().then((screen_filepath) => {
    var feedback_win = new remote.BrowserWindow({
      parent: remote.getCurrentWindow(),
      title: '问题反馈',
      modal: true,
      autoHideMenuBar: true,
      webPreferences: {
        nodeIntegration: true,
        javascript: true,
        enableRemoteModule: true,
      }
    })
    feedback_win.loadFile("core/html/feedback.html")
    feedback_win.addListener('ready-to-show', (event) => {
      log.info('feedbacktab finishload');
      ipcRenderer.sendTo(feedback_win.webContents.id, 'sys_screenshot', screen_filepath);
    })

    log.info("screenshot succ");
  })
}
feedback_btn.onclick = feedback;

function setting () {
  var setting_win = new remote.BrowserWindow({
    parent: remote.getCurrentWindow(),
    modal: true,
    autoHideMenuBar: true,
    webPreferences: {
      nodeIntegration: true,
      javascript: true,
      enableRemoteModule: true,
    }
  })
  setting_win.loadFile("core/html/setting.html")
  setting_win.addListener('ready-to-show', (event) => {
    log.info('feedbacktab finishload');
    // ipcRenderer.sendTo(setting_win.webContents.id, 'sys_screenshot', screen_filepath);
  })
}
setting_btn.onclick = setting;

var rigthTemplate = [
  { label: '粘贴' },
  { label: '复制' }
]

var m = remote.Menu.buildFromTemplate(rigthTemplate)

window.addEventListener('contextmenu', function (e) {
  e.preventDefault();
  m.popup({ window: remote.getCurrentWindow() })
})



function check_setting() {
  // setting_path = path.join(remote.process.cwd(), "config/config.xml")
  setting_path = "C:/HI-MXT_config.xml"
  log.info(setting_path);
  if (!fs.existsSync(setting_path)) {
    alert("请先配置系统设置");
    return false;
  }
  return true;
}
if (!check_setting()) {
  // setting();
}

var boardmgr;
function load_boardmgr()
{
  boardmgr = require('./boardmgr')
}

function check_app()
{
  log.info("start check_installed_app")
  boardmgr.thriftClient.check_installed_app((error, apps) => {
    log.info("check_installed_app ing")
    if (error) {
      log.info(error);
      alert("check_installed_app fail")
    } else{
      apps = JSON.parse(apps);
      for (var app of apps) {
        let app_btn = app + '_btn';
        $('#'+app_btn).attr("disabled",false);
        log.info(app + 'start ok')
      }
      log.info("check_installed_app ok")
    }
  })
}


function distribute_ws_msg(msg)
{
  var data = JSON.parse(msg);
  
  // ipcRenderer.sendTo(logexporttabid, data.comp_name, data.data);
  switch (data.comp_name) {
    case 'thrift':
      if (data.data == "") {
        load_boardmgr()
        check_app()
      }
      break;
    case 'boardmgr':
      log.info("boardmgr ws msg")
      boardmgr.change_board_state(data.data);
      break;

    case 'logexport':
      ipcRenderer.sendTo(logexporttabid, data.comp_name, data.data);
      break;
    
    case 'gettrace':
      ipcRenderer.sendTo(tracetabid, data.comp_name, data.data);
      break
    
    case 'sysview':
      ipcRenderer.sendTo(sysviewtabid, data.comp_name, data.data);
      break

    case 'bus_monitor':
      ipcRenderer.sendTo(bus_monitortabid, data.comp_name, data.data);
      break

    case 'ddrscan':
      ipcRenderer.sendTo(ddrscantabid, data.comp_name, data.data);
      break
  
    default:
      log.info("undefine comp name:" + data.comp_name)
      break;
  }
}


var ws = null;
var ws_connect_count = 0
function create_ws()
{
  var cnt = 0;
  ws_connect_count += 1;
  log.info("ws create", ws_connect_count);
  // ws = new WebSocket("ws://127.0.0.1:9998");
  ws = new WebSocket("ws://" + remote.getGlobal('IP') + ":" + remote.getGlobal('WSPORT'));
  ws.onopen = function () {
    log.info('WebSocket open');//成功连接上Websocket
    load_boardmgr()
    check_app()
    ws.send("channel open");
  };

  ws.onmessage = function (e) {
    //打印出服务端返回过来的数据
    // log.info('message: ' + e.data);
    distribute_ws_msg(e.data)
    cnt += 1;
    log.info("ws msg cnt: " + cnt.toString());
  };

  ws.onclose = function (e) {
    log.info("websocket closed")
  };

  ws.onerror = function (e) {
    ws.close();
    log.info(e);
    if (ws_connect_count < 5) {
      create_ws()
    } else {
      alert("websockket err");
    }
  }
}
create_ws();

ipcRenderer.on('ws_msg', (e, data) => {
  ws.send(data);
})

ipcRenderer.on('tab_fork', (e, msg) => {
  log.info('ipcmsg', msg)
  if (msg == 'logexport') {
    logexport_btn.onclick()
  } else if (msg == 'logparser') {
    logparser_btn.onclick()
  } else if (msg == 'trace') {
    trace_btn.onclick()
  } else if (msg == 'cycleview') {
    cycleview_btn.onclick()
  } else if (msg == 'ddrconfig') {
    ddrconfig_btn.onclick()
  } else if (msg == 'sysview') {
    sysview_btn.onclick()
  } else if (msg == 'ddrscan') {
    ddrscan_btn.onclick()
  } else if (msg == 'bus_monitor') {
    bus_monitor_btn.onclick()
  } else {
    log.info("tab fork fail")
    log.info(msg)
  }
});





ipcRenderer.on('open_new_logparser', (e, export_id, parser_num) => {
  log.info("open_new_logparser");
  let logparsertab = tabGroup.addTab({
    title: "日志解析",
    src: "apps/logparser/src/logparser.html",
    visible: true,
    active: true,
    webviewAttributes: { sourceMap: true, javaScriptEnabled: true, nodeIntegration: true, WebContentsDebuggingEnabled: true }
  })

  logparsertab.webview.addEventListener('did-finish-load', (event) => {
    log.info('logparsertab finishload2');
    let logparsertabid = logparsertab.webview.getWebContentsId();
    log.info("new logparsertabid " + logparsertabid);

    ipcRenderer.sendTo(export_id, 'logparser_opened', logparsertabid);
    logparsertab.on("active", (tab) => {
      log.info('logparsertab load')
      log.info("tab webcontentsid " + logparsertabid);
      ipcRenderer.sendTo(logparsertabid, "change_session", logparsertabid);
    });
  })
})
```

