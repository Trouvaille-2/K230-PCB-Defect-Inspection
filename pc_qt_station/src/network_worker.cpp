#include "network_worker.h"
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>//这三个库是官方自带的Json解析库
#include <QDebug>

//析构函数：初始化成员变量
NetworkWorker::NetworkWorker(quint16 port, QObject *parent)
    : QObject(parent), m_port(port), m_server(nullptr), m_socket(nullptr){
//初始化列表，把端口号服务端和客户端指针安全初始化为空指针
    }

//析构函数：释放资源，停止服务
NetworkWorker::~NetworkWorker() {
    stopServer();//调用停止服务函数，释放资源，杜绝端口被占用
}

void NetworkWorker::startServer(){
    m_server = new QTcpServer(this);//创建一个 TCP 服务端对象
    //当底层监听听到新设备连进来时，自动呼叫我们的接待函数onNewConnct
    connect(m_server,&QTcpServer::newConnection,this,&NetworkWorker::onNewConnection);

    //绑定端口并开启监听，
    if(m_server->listen(QHostAddress::Any,m_port)){
        emit logMessage(QString("[网络服务]工业监控服务端已启动，监听端口：%1").arg(m_port));
    }else {
        emit logMessage(QString("[网络错误]端口%1 监听失败 %2").arg(m_port).arg(m_server->errorString));
    }
    
}

void NetworkWorker::stopServer(){
    if(m_clientSocker){
        m_clientSocket->disconnectFromHost();
        m_clinetSocket = nullptr;//严防野指针
    }
    if(m_server){
        m_server->close();
        delete m_server;
        m_server = nullptr;
    }
}
