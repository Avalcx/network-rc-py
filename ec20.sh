#!/bin/bash

startEC20(){

QL_DEVNAME=/dev/ttyUSB3
QL_APN=3gnet
QL_USER=user
QL_PASSWORD=passwd


CONNECT="'chat -s -v ABORT BUSY ABORT \"NO CARRIER\" ABORT \"NO DIALTONE\" ABORT ERROR ABORT \"NO ANSWER\" TIMEOUT 30 \
	\"\" AT OK ATE0 OK ATI\;+CSUB\;+CSQ\;+CPIN?\;+COPS?\;+CGREG?\;\&D2 \
	OK AT+CGDCONT=1,\\\"IP\\\",\\\"$QL_APN\\\",,0,0 OK ATD*99# CONNECT'"
pppd $QL_DEVNAME 115200 user "$QL_USER" password "$QL_PASSWORD" \
connect "'$CONNECT'" \
disconnect 'chat -s -v ABORT ERROR ABORT "NO DIALTONE" SAY "\nSending break to the modem\n" "" +++ "" +++ "" +++ SAY "\nGood bay\n"' \
noauth debug defaultroute noipdefault novj novjccomp noccp ipcp-accept-local ipcp-accept-remote ipcp-max-configure 30 local lock modem dump nodetach nocrtscts usepeerdns &

}


stopEC20(){
  timeout=5
  killall -15 pppd
  sleep 1
  killall -0 pppd
  while [ $? -eq 0 ];do
    timeout=`expr $timeout - 1`
    if [ $timeout -eq 0 ];then
       exit 1
    fi
    sleep 1
    killall -0 pppd
  done

  if [ $? -ne 0 ];then
     killall -9 pppd
  fi
}

printStart(){
  echo "------------"
  echo "ec20 start!" 
  echo "------------"
}

printStop(){
  echo "------------"
  echo "ec20 stop!" 
  echo "------------"
}


CHECK=`ifconfig | grep -o "ppp0"`

if [[ $1 == "start" ]];then
   echo "$CHECK"
   if [[ $CHECK == "ppp0" ]];then
      stopEC20 >/dev/null 2&>1
      sleep 2
      startEC20  >/dev/null 2&>1
   else
      startEC20  >/dev/null 2&>1
   fi

   until [[ $CHECK == "ppp0" ]];do
	echo "$CHECK"
        printStart;
	break
   done

elif [[ $1 == "stop" ]];then
   stopEC20 >/dev/null 2&>1 
   printStop;
else
   echo "--------------------------"
   echo "please input start or stop"
   echo "--------------------------"
fi
