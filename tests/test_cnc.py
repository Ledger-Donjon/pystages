import logging
import time
from typing import Callable

from pystages import Vector
from pystages.cncrouter import CNCRouter

def test_init(require_stage: Callable[[str], None], stage_dev: str | None):
    require_stage("CNC")
    cnc = CNCRouter(dev=stage_dev, do_reset=False)
    print(cnc.atr)
    print(cnc.position)
    print(cnc.get_current_status())
    cnc.unlock()
    cnc.unlock()
    cnc.unlock()
    cnc.unlock()
    cnc.unlock()
    print(cnc.get_current_status())
    print(cnc.get_current_status())
    print(cnc.get_current_status())
    print(cnc.get_current_status())
    print(cnc.get_current_status())
    print(cnc.get_current_status())
    print(cnc.get_current_status())
    print(cnc.get_current_status())
    print(cnc.get_current_status())
    print(cnc.get_current_status())
    print(cnc.get_current_status())

def test_init_reset(require_stage: Callable[[str], None], stage_dev: str | None):
    require_stage("CNC")
    cnc = CNCRouter(dev=stage_dev, do_reset=True)
    print(cnc.atr)
    print(cnc.position)
    print(cnc.get_current_status())


def test_home(require_stage: Callable[[str], None], stage_dev: str | None):
    require_stage("CNC")
    cnc = CNCRouter(dev=stage_dev, do_reset=False)
    time.sleep(1)
    print(cnc.get_current_status())
    cnc.home(wait=False)
    time.sleep(60)
    print(cnc.get_current_status())

def test_get_position(require_stage: Callable[[str], None], stage_dev: str | None):
    require_stage("CNC")
    cnc = CNCRouter(dev=stage_dev, do_reset=False)
    cnc.logger.setLevel(logging.DEBUG)
    print(cnc.position)
    print(cnc.get_current_status())
    cnc.unlock()
    print(cnc.get_current_status())
    print(cnc.position)

    # cnc.position = Vector(10, 10, 10)
    # print(cnc.position)
    # print(cnc.get_current_status())
    # cnc.position = Vector(20, 20, 20)
    # print(cnc.position)
    # print(cnc.get_current_status())