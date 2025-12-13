// 触摸手势处理工具
export interface TouchPoint {
  id: number
  x: number
  y: number
  timestamp: number
}

export interface GestureEvent {
  type: 'tap' | 'double-tap' | 'long-press' | 'pinch' | 'pan' | 'swipe' | 'rotate'
  touches: TouchPoint[]
  center: { x: number; y: number }
  scale?: number
  rotation?: number
  velocity?: { x: number; y: number }
  direction?: 'up' | 'down' | 'left' | 'right'
  distance?: number
  duration?: number
  preventDefault: () => void
  stopPropagation: () => void
}

export interface GestureConfig {
  // 基础配置
  enableTap: boolean
  enableDoubleTap: boolean
  enableLongPress: boolean
  enablePinch: boolean
  enablePan: boolean
  enableSwipe: boolean
  enableRotate: boolean
  
  // 阈值配置
  tapTimeout: number
  doubleTapTimeout: number
  longPressTimeout: number
  moveThreshold: number
  swipeThreshold: number
  swipeVelocityThreshold: number
  pinchThreshold: number
  rotateThreshold: number
  
  // 灵敏度配置
  panSensitivity: number
  pinchSensitivity: number
  rotateSensitivity: number
  
  // 其他配置
  preventDefaultEvents: boolean
  stopPropagationEvents: boolean
}

export interface GestureCallbacks {
  onTap?: (event: GestureEvent) => void
  onDoubleTap?: (event: GestureEvent) => void
  onLongPress?: (event: GestureEvent) => void
  onPinchStart?: (event: GestureEvent) => void
  onPinch?: (event: GestureEvent) => void
  onPinchEnd?: (event: GestureEvent) => void
  onPanStart?: (event: GestureEvent) => void
  onPan?: (event: GestureEvent) => void
  onPanEnd?: (event: GestureEvent) => void
  onSwipe?: (event: GestureEvent) => void
  onRotateStart?: (event: GestureEvent) => void
  onRotate?: (event: GestureEvent) => void
  onRotateEnd?: (event: GestureEvent) => void
}

// 默认配置
const defaultConfig: GestureConfig = {
  enableTap: true,
  enableDoubleTap: true,
  enableLongPress: true,
  enablePinch: true,
  enablePan: true,
  enableSwipe: true,
  enableRotate: true,
  
  tapTimeout: 300,
  doubleTapTimeout: 300,
  longPressTimeout: 500,
  moveThreshold: 10,
  swipeThreshold: 50,
  swipeVelocityThreshold: 0.5,
  pinchThreshold: 0.1,
  rotateThreshold: 5,
  
  panSensitivity: 1.0,
  pinchSensitivity: 1.0,
  rotateSensitivity: 1.0,
  
  preventDefaultEvents: true,
  stopPropagationEvents: false
}

export class TouchGestureHandler {
  private element: HTMLElement
  private config: GestureConfig
  private callbacks: GestureCallbacks
  
  // 状态管理
  private touches: Map<number, TouchPoint> = new Map()
  private gestureState = {
    isActive: false,
    startTime: 0,
    lastTapTime: 0,
    tapCount: 0,
    initialDistance: 0,
    initialAngle: 0,
    initialCenter: { x: 0, y: 0 },
    lastCenter: { x: 0, y: 0 },
    lastScale: 1,
    lastRotation: 0,
    isPinching: false,
    isPanning: false,
    isRotating: false,
    longPressTimer: null as number | null
  }
  
  constructor(
    element: HTMLElement,
    callbacks: GestureCallbacks,
    config: Partial<GestureConfig> = {}
  ) {
    this.element = element
    this.callbacks = callbacks
    this.config = { ...defaultConfig, ...config }
    
    this.bindEvents()
  }
  
  private bindEvents() {
    this.element.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false })
    this.element.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false })
    this.element.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: false })
    this.element.addEventListener('touchcancel', this.handleTouchCancel.bind(this), { passive: false })
  }
  
  private unbindEvents() {
    this.element.removeEventListener('touchstart', this.handleTouchStart.bind(this))
    this.element.removeEventListener('touchmove', this.handleTouchMove.bind(this))
    this.element.removeEventListener('touchend', this.handleTouchEnd.bind(this))
    this.element.removeEventListener('touchcancel', this.handleTouchCancel.bind(this))
  }
  
  private handleTouchStart(event: TouchEvent) {
    const now = Date.now()
    
    // 更新触摸点
    for (let i = 0; i < event.changedTouches.length; i++) {
      const touch = event.changedTouches[i]
      this.touches.set(touch.identifier, {
        id: touch.identifier,
        x: touch.clientX,
        y: touch.clientY,
        timestamp: now
      })
    }
    
    const touchCount = this.touches.size
    
    if (touchCount === 1) {
      this.handleSingleTouchStart(event, now)
    } else if (touchCount === 2) {
      this.handleMultiTouchStart(event, now)
    }
    
    this.gestureState.isActive = true
    this.gestureState.startTime = now
    
    if (this.config.preventDefaultEvents) {
      event.preventDefault()
    }
    if (this.config.stopPropagationEvents) {
      event.stopPropagation()
    }
  }
  
  private handleSingleTouchStart(event: TouchEvent, timestamp: number) {
    const touch = event.changedTouches[0]
    
    // 长按检测
    if (this.config.enableLongPress) {
      this.gestureState.longPressTimer = window.setTimeout(() => {
        this.triggerLongPress(touch, timestamp)
      }, this.config.longPressTimeout)
    }
    
    // 双击检测
    if (this.config.enableDoubleTap) {
      const timeSinceLastTap = timestamp - this.gestureState.lastTapTime
      
      if (timeSinceLastTap < this.config.doubleTapTimeout) {
        this.gestureState.tapCount++
      } else {
        this.gestureState.tapCount = 1
      }
    }
  }
  
  private handleMultiTouchStart(event: TouchEvent, timestamp: number) {
    if (event.touches.length === 2) {
      const touch1 = event.touches[0]
      const touch2 = event.touches[1]
      
      // 计算初始距离和角度
      this.gestureState.initialDistance = this.getDistance(touch1, touch2)
      this.gestureState.initialAngle = this.getAngle(touch1, touch2)
      this.gestureState.initialCenter = this.getCenter(touch1, touch2)
      this.gestureState.lastCenter = { ...this.gestureState.initialCenter }
      this.gestureState.lastScale = 1
      this.gestureState.lastRotation = 0
      
      // 清除长按定时器
      if (this.gestureState.longPressTimer) {
        clearTimeout(this.gestureState.longPressTimer)
        this.gestureState.longPressTimer = null
      }
    }
  }
  
  private handleTouchMove(event: TouchEvent) {
    if (!this.gestureState.isActive) return
    
    const now = Date.now()
    
    // 更新触摸点
    for (let i = 0; i < event.changedTouches.length; i++) {
      const touch = event.changedTouches[i]
      const existingTouch = this.touches.get(touch.identifier)
      
      if (existingTouch) {
        // 检查是否超过移动阈值
        const distance = this.getPointDistance(
          { x: existingTouch.x, y: existingTouch.y },
          { x: touch.clientX, y: touch.clientY }
        )
        
        if (distance > this.config.moveThreshold) {
          // 清除长按定时器
          if (this.gestureState.longPressTimer) {
            clearTimeout(this.gestureState.longPressTimer)
            this.gestureState.longPressTimer = null
          }
        }
        
        this.touches.set(touch.identifier, {
          id: touch.identifier,
          x: touch.clientX,
          y: touch.clientY,
          timestamp: now
        })
      }
    }
    
    const touchCount = this.touches.size
    
    if (touchCount === 1) {
      this.handleSingleTouchMove(event, now)
    } else if (touchCount === 2) {
      this.handleMultiTouchMove(event, now)
    }
    
    if (this.config.preventDefaultEvents) {
      event.preventDefault()
    }
    if (this.config.stopPropagationEvents) {
      event.stopPropagation()
    }
  }
  
  private handleSingleTouchMove(event: TouchEvent, timestamp: number) {
    if (!this.config.enablePan) return
    
    const touch = event.changedTouches[0]
    const touchPoint = this.touches.get(touch.identifier)
    
    if (!touchPoint) return
    
    if (!this.gestureState.isPanning) {
      this.gestureState.isPanning = true
      this.triggerPanStart(touch, timestamp)
    }
    
    this.triggerPan(touch, timestamp)
  }
  
  private handleMultiTouchMove(event: TouchEvent, timestamp: number) {
    if (event.touches.length !== 2) return
    
    const touch1 = event.touches[0]
    const touch2 = event.touches[1]
    
    const currentDistance = this.getDistance(touch1, touch2)
    const currentAngle = this.getAngle(touch1, touch2)
    const currentCenter = this.getCenter(touch1, touch2)
    
    // 缩放检测
    if (this.config.enablePinch && this.gestureState.initialDistance > 0) {
      const scale = currentDistance / this.gestureState.initialDistance
      const scaleDelta = Math.abs(scale - this.gestureState.lastScale)
      
      if (scaleDelta > this.config.pinchThreshold) {
        if (!this.gestureState.isPinching) {
          this.gestureState.isPinching = true
          this.triggerPinchStart(touch1, touch2, timestamp)
        }
        
        this.triggerPinch(touch1, touch2, scale, timestamp)
        this.gestureState.lastScale = scale
      }
    }
    
    // 旋转检测
    if (this.config.enableRotate) {
      const rotation = currentAngle - this.gestureState.initialAngle
      const rotationDelta = Math.abs(rotation - this.gestureState.lastRotation)
      
      if (rotationDelta > this.config.rotateThreshold) {
        if (!this.gestureState.isRotating) {
          this.gestureState.isRotating = true
          this.triggerRotateStart(touch1, touch2, timestamp)
        }
        
        this.triggerRotate(touch1, touch2, rotation, timestamp)
        this.gestureState.lastRotation = rotation
      }
    }
    
    this.gestureState.lastCenter = currentCenter
  }
  
  private handleTouchEnd(event: TouchEvent) {
    const now = Date.now()
    
    // 移除结束的触摸点
    for (let i = 0; i < event.changedTouches.length; i++) {
      const touch = event.changedTouches[i]
      this.touches.delete(touch.identifier)
    }
    
    const remainingTouches = this.touches.size
    
    if (remainingTouches === 0) {
      this.handleAllTouchesEnd(event, now)
    } else if (remainingTouches === 1 && this.gestureState.isPinching) {
      // 从双指变为单指
      this.handlePinchEnd(event, now)
    }
    
    if (this.config.preventDefaultEvents) {
      event.preventDefault()
    }
    if (this.config.stopPropagationEvents) {
      event.stopPropagation()
    }
  }
  
  private handleAllTouchesEnd(event: TouchEvent, timestamp: number) {
    const duration = timestamp - this.gestureState.startTime
    
    // 清除长按定时器
    if (this.gestureState.longPressTimer) {
      clearTimeout(this.gestureState.longPressTimer)
      this.gestureState.longPressTimer = null
    }
    
    // 处理点击事件
    if (!this.gestureState.isPanning && !this.gestureState.isPinching && !this.gestureState.isRotating) {
      if (duration < this.config.tapTimeout) {
        this.handleTapGesture(event, timestamp)
      }
    }
    
    // 处理滑动事件
    if (this.gestureState.isPanning && this.config.enableSwipe) {
      this.handleSwipeGesture(event, timestamp, duration)
    }
    
    // 结束手势
    if (this.gestureState.isPanning) {
      this.triggerPanEnd(event.changedTouches[0], timestamp)
    }
    
    if (this.gestureState.isPinching) {
      this.triggerPinchEnd(event.changedTouches[0], timestamp)
    }
    
    if (this.gestureState.isRotating) {
      this.triggerRotateEnd(event.changedTouches[0], timestamp)
    }
    
    this.resetGestureState()
  }
  
  private handleTapGesture(event: TouchEvent, timestamp: number) {
    const touch = event.changedTouches[0]
    
    if (this.config.enableDoubleTap && this.gestureState.tapCount >= 2) {
      this.triggerDoubleTap(touch, timestamp)
      this.gestureState.tapCount = 0
    } else if (this.config.enableTap) {
      // 延迟触发单击，等待可能的双击
      setTimeout(() => {
        if (this.gestureState.tapCount === 1) {
          this.triggerTap(touch, timestamp)
          this.gestureState.tapCount = 0
        }
      }, this.config.doubleTapTimeout)
    }
    
    this.gestureState.lastTapTime = timestamp
  }
  
  private handleSwipeGesture(event: TouchEvent, timestamp: number, duration: number) {
    const touch = event.changedTouches[0]
    const startTouch = Array.from(this.touches.values())[0]
    
    if (!startTouch) return
    
    const deltaX = touch.clientX - startTouch.x
    const deltaY = touch.clientY - startTouch.y
    const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY)
    const velocity = distance / duration
    
    if (distance > this.config.swipeThreshold && velocity > this.config.swipeVelocityThreshold) {
      let direction: 'up' | 'down' | 'left' | 'right'
      
      if (Math.abs(deltaX) > Math.abs(deltaY)) {
        direction = deltaX > 0 ? 'right' : 'left'
      } else {
        direction = deltaY > 0 ? 'down' : 'up'
      }
      
      this.triggerSwipe(touch, direction, velocity, distance, timestamp)
    }
  }
  
  private handlePinchEnd(event: TouchEvent, timestamp: number) {
    if (this.gestureState.isPinching) {
      this.triggerPinchEnd(event.changedTouches[0], timestamp)
    }
    
    if (this.gestureState.isRotating) {
      this.triggerRotateEnd(event.changedTouches[0], timestamp)
    }
    
    this.gestureState.isPinching = false
    this.gestureState.isRotating = false
  }
  
  private handleTouchCancel(event: TouchEvent) {
    this.touches.clear()
    this.resetGestureState()
    
    if (this.config.preventDefaultEvents) {
      event.preventDefault()
    }
  }
  
  private resetGestureState() {
    this.gestureState.isActive = false
    this.gestureState.isPanning = false
    this.gestureState.isPinching = false
    this.gestureState.isRotating = false
    
    if (this.gestureState.longPressTimer) {
      clearTimeout(this.gestureState.longPressTimer)
      this.gestureState.longPressTimer = null
    }
  }
  
  // 触发手势事件的方法
  private triggerTap(touch: Touch, timestamp: number) {
    if (!this.callbacks.onTap) return
    
    const event = this.createGestureEvent('tap', [this.touchToPoint(touch, timestamp)])
    this.callbacks.onTap(event)
  }
  
  private triggerDoubleTap(touch: Touch, timestamp: number) {
    if (!this.callbacks.onDoubleTap) return
    
    const event = this.createGestureEvent('double-tap', [this.touchToPoint(touch, timestamp)])
    this.callbacks.onDoubleTap(event)
  }
  
  private triggerLongPress(touch: Touch, timestamp: number) {
    if (!this.callbacks.onLongPress) return
    
    const event = this.createGestureEvent('long-press', [this.touchToPoint(touch, timestamp)])
    this.callbacks.onLongPress(event)
  }
  
  private triggerPanStart(touch: Touch, timestamp: number) {
    if (!this.callbacks.onPanStart) return
    
    const event = this.createGestureEvent('pan', [this.touchToPoint(touch, timestamp)])
    this.callbacks.onPanStart(event)
  }
  
  private triggerPan(touch: Touch, timestamp: number) {
    if (!this.callbacks.onPan) return
    
    const event = this.createGestureEvent('pan', [this.touchToPoint(touch, timestamp)])
    this.callbacks.onPan(event)
  }
  
  private triggerPanEnd(touch: Touch, timestamp: number) {
    if (!this.callbacks.onPanEnd) return
    
    const event = this.createGestureEvent('pan', [this.touchToPoint(touch, timestamp)])
    this.callbacks.onPanEnd(event)
  }
  
  private triggerPinchStart(touch1: Touch, touch2: Touch, timestamp: number) {
    if (!this.callbacks.onPinchStart) return
    
    const touches = [
      this.touchToPoint(touch1, timestamp),
      this.touchToPoint(touch2, timestamp)
    ]
    const event = this.createGestureEvent('pinch', touches)
    event.scale = 1
    this.callbacks.onPinchStart(event)
  }
  
  private triggerPinch(touch1: Touch, touch2: Touch, scale: number, timestamp: number) {
    if (!this.callbacks.onPinch) return
    
    const touches = [
      this.touchToPoint(touch1, timestamp),
      this.touchToPoint(touch2, timestamp)
    ]
    const event = this.createGestureEvent('pinch', touches)
    event.scale = scale
    this.callbacks.onPinch(event)
  }
  
  private triggerPinchEnd(touch: Touch, timestamp: number) {
    if (!this.callbacks.onPinchEnd) return
    
    const event = this.createGestureEvent('pinch', [this.touchToPoint(touch, timestamp)])
    this.callbacks.onPinchEnd(event)
  }
  
  private triggerRotateStart(touch1: Touch, touch2: Touch, timestamp: number) {
    if (!this.callbacks.onRotateStart) return
    
    const touches = [
      this.touchToPoint(touch1, timestamp),
      this.touchToPoint(touch2, timestamp)
    ]
    const event = this.createGestureEvent('rotate', touches)
    event.rotation = 0
    this.callbacks.onRotateStart(event)
  }
  
  private triggerRotate(touch1: Touch, touch2: Touch, rotation: number, timestamp: number) {
    if (!this.callbacks.onRotate) return
    
    const touches = [
      this.touchToPoint(touch1, timestamp),
      this.touchToPoint(touch2, timestamp)
    ]
    const event = this.createGestureEvent('rotate', touches)
    event.rotation = rotation
    this.callbacks.onRotate(event)
  }
  
  private triggerRotateEnd(touch: Touch, timestamp: number) {
    if (!this.callbacks.onRotateEnd) return
    
    const event = this.createGestureEvent('rotate', [this.touchToPoint(touch, timestamp)])
    this.callbacks.onRotateEnd(event)
  }
  
  private triggerSwipe(
    touch: Touch,
    direction: 'up' | 'down' | 'left' | 'right',
    velocity: number,
    distance: number,
    timestamp: number
  ) {
    if (!this.callbacks.onSwipe) return
    
    const event = this.createGestureEvent('swipe', [this.touchToPoint(touch, timestamp)])
    event.direction = direction
    event.velocity = { x: velocity, y: velocity }
    event.distance = distance
    this.callbacks.onSwipe(event)
  }
  
  // 工具方法
  private createGestureEvent(type: GestureEvent['type'], touches: TouchPoint[]): GestureEvent {
    const center = this.getTouchesCenter(touches)
    
    return {
      type,
      touches,
      center,
      preventDefault: () => {},
      stopPropagation: () => {}
    }
  }
  
  private touchToPoint(touch: Touch, timestamp: number): TouchPoint {
    return {
      id: touch.identifier,
      x: touch.clientX,
      y: touch.clientY,
      timestamp
    }
  }
  
  private getDistance(touch1: Touch, touch2: Touch): number {
    const dx = touch1.clientX - touch2.clientX
    const dy = touch1.clientY - touch2.clientY
    return Math.sqrt(dx * dx + dy * dy)
  }
  
  private getAngle(touch1: Touch, touch2: Touch): number {
    const dx = touch1.clientX - touch2.clientX
    const dy = touch1.clientY - touch2.clientY
    return Math.atan2(dy, dx) * 180 / Math.PI
  }
  
  private getCenter(touch1: Touch, touch2: Touch): { x: number; y: number } {
    return {
      x: (touch1.clientX + touch2.clientX) / 2,
      y: (touch1.clientY + touch2.clientY) / 2
    }
  }
  
  private getPointDistance(point1: { x: number; y: number }, point2: { x: number; y: number }): number {
    const dx = point1.x - point2.x
    const dy = point1.y - point2.y
    return Math.sqrt(dx * dx + dy * dy)
  }
  
  private getTouchesCenter(touches: TouchPoint[]): { x: number; y: number } {
    if (touches.length === 0) return { x: 0, y: 0 }
    
    const sum = touches.reduce(
      (acc, touch) => ({
        x: acc.x + touch.x,
        y: acc.y + touch.y
      }),
      { x: 0, y: 0 }
    )
    
    return {
      x: sum.x / touches.length,
      y: sum.y / touches.length
    }
  }
  
  // 公共方法
  public updateConfig(config: Partial<GestureConfig>) {
    this.config = { ...this.config, ...config }
  }
  
  public destroy() {
    this.unbindEvents()
    this.resetGestureState()
    this.touches.clear()
  }
  
  public isGestureActive(): boolean {
    return this.gestureState.isActive
  }
  
  public getCurrentTouches(): TouchPoint[] {
    return Array.from(this.touches.values())
  }
}

// 便捷函数
export function createTouchGestureHandler(
  element: HTMLElement,
  callbacks: GestureCallbacks,
  config?: Partial<GestureConfig>
): TouchGestureHandler {
  return new TouchGestureHandler(element, callbacks, config)
}

// 预设配置
export const gesturePresets = {
  // 基础手势（点击、长按）
  basic: {
    enableTap: true,
    enableDoubleTap: true,
    enableLongPress: true,
    enablePinch: false,
    enablePan: false,
    enableSwipe: false,
    enableRotate: false
  } as Partial<GestureConfig>,
  
  // 图片查看器
  imageViewer: {
    enableTap: true,
    enableDoubleTap: true,
    enablePinch: true,
    enablePan: true,
    enableSwipe: true,
    enableRotate: false,
    pinchSensitivity: 0.8,
    panSensitivity: 1.2
  } as Partial<GestureConfig>,
  
  // 地图应用
  map: {
    enableTap: true,
    enablePinch: true,
    enablePan: true,
    enableSwipe: false,
    enableRotate: true,
    pinchSensitivity: 1.0,
    panSensitivity: 1.0,
    rotateSensitivity: 0.8
  } as Partial<GestureConfig>,
  
  // 游戏应用
  game: {
    enableTap: true,
    enableDoubleTap: false,
    enableLongPress: true,
    enablePinch: false,
    enablePan: true,
    enableSwipe: true,
    enableRotate: false,
    panSensitivity: 1.5,
    swipeVelocityThreshold: 0.3
  } as Partial<GestureConfig>
}