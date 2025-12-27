import asyncio
from mavsdk import System
from mavsdk.offboard import OffboardError, PositionNedYaw

async def run():
    # 1. 드론 객체 생성 & 연결
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("🔄 드론 연결 대기 중...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("드론 연결 완료")
            break

    # 2. ARM
    print("🟢 ARM 시도")
    await drone.action.arm()

    # 3. Offboard 시작 전 초기 setpoint (필수)
    print("📡 초기 위치 setpoint 전송")
    await drone.offboard.set_position_ned(
        PositionNedYaw(
            north_m=0.0,
            east_m=0.0,
            down_m=-2.0,  # 고도 2m (NED라 음수)
            yaw_deg=0.0
        )
    )

    # 4. Offboard 모드 시작
    print("🚀 Offboard 모드 시작")
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"❌ Offboard 시작 실패: {error}")
        await drone.action.disarm()
        return

    # 5. Takeoff + Hover
    print("⬆ 이륙 및 호버 (2m, 5초)")
    await asyncio.sleep(5)

    # 6. Land
    print("⬇ 착륙")
    await drone.action.land()

    await asyncio.sleep(5)

    # 7. Disarm
    print("🔴 DISARM")
    await drone.action.disarm()

    print("🎉 미션 완료 (Arm / Takeoff / Hover / Land)")

if __name__ == "__main__":
    asyncio.run(run())