# RainMind - Schedule Alarm System (FastAPI)  
  
## 1. Project 개요  
일정(Schedule) 생성 시 알림을 자동으로 예약(30분 전)하고, 지정된 시각에 알림을 출력하는 서비스입니다.  
  
Spring 기반 프로젝트이던 기존의 RainMind의 Schedule part를 FastAPI에서 구현하였습니다. Outbox pattern / Redis ZSet / Lua Script 이용 atomic operation을 FastAPI 환경으로 1:1 변환하는 것을 목표하였습니다. 
  
원본 Spring 프로젝트 링크는 아래와 같습니다.  
https://github.com/LOV-ING-U/project_rainmind  

## 2. 시스템 흐름
1) Client: POST /schedules  
2) Schedule + Outbox(status = PENDING) 저장 with transaction  
3) event_publisher가 PENDING Outbox를 조회 후, redis zset에 알람 등록(score = alarm 시각)  
4) worker가 Lua script 이용한 atomic zset dequeue로 알람 1개 pop  
5) 알람 출력  
  
## 3. 문제 정의 및 해결  
일정 생성 후 알람을 redis에 등록하면 아래와 같은 redis와 DB의 데이터가 일치하지 않는 정합성 문제가 발생할 수 있습니다.  
  
1) DB에 일정 삽입에 성공했으나, redis 알람 등록에 실패한 경우: 알람이 유실됩니다.  
2) Redis에 알람이 등록되었지만, DB 삽입은 실패한 경우: 유령 알람이 발생합니다.  
3) Worker 여러 대가 동시에 redis를 보며 일정 확인을 위해 dequeue할 경우: 중복 알람 혹은 예기치 못한 동작이 발생합니다.  
  
해당 프로젝트는 사용자가 알람을 등록할 때 발생하는 데이터 정합성 문제를 해결하기 위해 Outbox pattern을 적용합니다.  
  
DB와 redis를 완벽히 동기화시키는 것은 불가능합니다. 따라서 서비스 설계 목적 상, 알람 유실이 유령 알람/중복 알람보다 치명적이기 때문에 알람 유실을 막기 위해 Outbox pattern을 적용합니다.  
  
## 4. 왜 Outbox pattern을 사용했는가?  
DB와 redis의 완전한 데이터 정합성 유지는 트랜잭션으로 그 작업들을 묶을 수 없으므로 현실적으로 불가능합니다. 따라서  
  
1) 별도의 Outbox 테이블을 만들고, 일정 등록과 동시에 Outbox 테이블에 pending signal로서 해당 일정을 하나의 트랜잭션으로 저장  
2) Redis 등록 후 outbox 상태를 변경  
3) 별도의 Worker가 주기적으로 pending signal을 redis에 등록  
  
하게 된다면, DB나 Redis 둘 중 하나가 실패해도 알람이 유실되지 않고, 시스템 재시작 후에도 DB의 데이터를 통해 작업 수행이 이어서 가능합니다.  
  
## 5. 정합성  
- DB 정합성: Schedule, Outbox는 함께 Transaction 수행  
- Redis 미반영: Outbox 기반 event publisher의 지속적 재시도로 반영됨  
- Redis 알람 중복 dequeue 방지: Lua script 이용  
  
- 전체 구조: Redis 중복 enqueue 가능성 존재(알람의 payload가 다르다면), Redis dequeue 이후 알람 유실 가능  
  
전체적으로 모델 설계로 인한 알람 유실 문제는 해결하였고, 서비스 설계 특성상 유실이 중복보다 심각한 문제이므로 trade off를 선택했습니다.  
필요시 아래와 같은 확장이 가능합니다.  
  
- Outbox status를 deleted 등 확장하여 알람 삭제 기능 지원  
- 별도의 Kafka 등 메시지 브로커 사용
  
## 6. 기술 스택  
<p>
    <img alt="fastapi"  src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi">
</p>
<p>
    <img alt="redis"  src="https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white">
</p>
<p>
    <img alt="lua"  src="https://img.shields.io/badge/lua-%232C2D72.svg?style=for-the-badge&logo=lua&logoColor=white">
</p>  
<p>
    <img alt="docker"  src="https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white">
</p>  
  
## 7. 실행 방법  
FastAPI의 AsyncClient를 이용하여 실제 router를 호출한 후 schedule/outbox 생성 및 event_publisher의 redis enqueue 동작, 그리고 worker의 redis dequeue 동작을 검증하는 테스트코드를 작성했습니다.  
  
1) docker 실행  
2) image 만들기  
docker compose -f docker-compose.test.yml build --no-cache  
3) container 실행  
docker compose -f docker-compose.test.yml up --abort-on-container-exit