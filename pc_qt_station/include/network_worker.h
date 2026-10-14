#ifndef NETWORK_WORKER_H
#define NETWORK_WORKER_H

#include <QObject>
#include <QTcpServer>
#include <QTcpSocket>
#include <QByteArray>
#include <QImage>
#include <vector>
#include "protocol.h"

//接收到完整质检帧后发给UI的数据包
struct InspectionFrameData{
    uint32_t seq;//帧序号
    QImage image;//K230摄像头拍下来的PCB照片
    std::vector<DefectItem> defects;
};

class NetworkWorker : public QObject
{
    Q_OBJECT
public:
    explicit NetworkWorker(quint16 port = 8554,QObject *parent = nullptr);
    ~NetworkWorker();

public slots:
    void startServer();
    void stopServer();

signals:
    void clientConnected(const QString &clientAddress);//有新边缘板接入了，把板子的 IP 和端口号喊给主界面
    void clientDisconnected();//板子断开连接了，喊一声让主界面把状态灯变成灰色
    void frameReceived(const InspectionFrameData &frame);全系统最核心信号！ 当在后台把图片和缺陷检测数据拼好成一个完整的 frame 包裹时，喊一声把包裹直接“快递”给 UI 界面去画图。
    void logMessage(const QString &msg);//产生了一条系统日志文本，喊一声让主界面的黑底控制台打出来

private slots:
    void onNewConnection();//：当网卡监听到有 K230 板子建立 TCP 握手时，底层的 QTcpServer 会触发这个函数。
    void onReadyRead();//网络数据流动的心脏！ 当网线里有新的二进制字节飞过来时，底层的 Socket 会触发这个函数
    void onSocketDisconnected();//当 K230 关机或者网线被拔掉时，底层的 Socket 会触发这个函数，通知我们做善后清理。

private:
    void processBuffer();

    quint16 m_port;
    QTcpServer *m_server;
    QTcpSocket *m_socket;
    QByteArray m_rxBuffer;
};

#endif // NETWORK_WORKER_H