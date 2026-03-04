# 源代码提交页（智能楼宇会议室系统 buildingos.meetingroom）

## 提交要求
- 连续前30页与后30页，每页≥50行
- 不得包含公司、个人、文件名称
- 数量与申请表一致

## 前30页
```
<template>
  <div class="meetingroom-container no-background-container auto-height-container">
   <el-row :gutter="20">
      <el-col :lg="5" :md="24" :sm="24" :xl="4" :xs="24">
        <vab-card class="auto-height-card1">
          <!-- 添加日期选择器 -->
          <div class="date-selector">
            <el-date-picker
              v-model="showDay"
              type="date"
              placeholder="选择日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="updateCalendarDate"
            />
          </div>
          <el-tree
            ref="treeRef"
            v-loading="treeLoading"
            :data="spacedata"
            default-expand-all
            :highlight-current="true"
            node-key="id"
            :props="defaultProps"
            @node-click="handleNodeClick"
          />
        </vab-card>
      </el-col>
        <el-col :lg="19" :md="24" :sm="24" :xl="20" :xs="24">
            <full-calendar 
              ref="fullCalendar"
              class="demo-app-calendar" 
              :options="calendarOptions">
              <template #eventContent="arg">
                <b>{{ arg.timeText }}</b>
                <!-- <i>{{ arg.event.title }}</i> -->
              </template>
            </full-calendar>
            
            <!-- Meeting Form Drawer -->
            <meeting-form
              v-model="showDrawer"
              :event-data="currentEvent"
              :is-edit="isEditMode"
              :resources="calendarOptions.resources" 
              @submit="handleFormSubmit"
              @fetach="fetchData"
              @close="resetForm"
            />
        </el-col>
      </el-row>
  </div>
</template>
<script>
import { defineComponent, ref } from 'vue'
import FullCalendar from '@fullcalendar/vue3'
import resourceTimelinePlugin from '@fullcalendar/resource-timeline'
import resourceTimeGridPlugin from '@fullcalendar/resource-timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import zhLocale from '@fullcalendar/core/locales/zh-cn'
import MeetingForm from './MeetingForm.vue'
import { getTreeByFloor } from '/@/api/spaceManagement.ts'
import { getMeetingList,saveSchedule, getMList} from '/@/api/sence.ts'
import { getMRoomList } from '/@/api/space.ts'
import { useUserStore } from '/@/store/modules/user'

const userStore = useUserStore()
const {userId, username,departmentName,departmentId,orgId,orgName } = storeToRefs(userStore)
console.log('username', username.value)

import moment from 'moment/moment'
import user from '~/mock/controller/user'
export default defineComponent({
  components: {
    FullCalendar,
    MeetingForm
  },
  data() {
    return {
      // $baseMessage : inject('$baseMessage'),
      getListObj: [],
      showDay: moment().format('YYYY-MM-DD'),
      treeLoading: true,
      showDrawer: false,
      isEditMode: false,
      currentEvent: {},
      spacedata: [],
      roomlist: [],
      queryForm: {
        spaceCode: '',
        floorAreaCode: '',
        floorCode: '',
        areaCode: '',
        areaType: '',
        pageNo: 1,
        pageSize: 500,
        title: '',
      },
      defaultProps: {
        children: 'children',
        label: 'label',
      },
      calendarOptions: {
        locales: [zhLocale],
        locale: 'zh',
        schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',
        plugins: [
          resourceTimeGridPlugin, 
          resourceTimelinePlugin,
          interactionPlugin,
          dayGridPlugin,
          timeGridPlugin
        ],
        headerToolbar: {
          left: 'today prev,next',
          center: 'title',
          right: 'resourceTimeGridDay,resourceTimeGridWeek',
        },
        buttonText: {
          today: '今天',
          week: '周视图',
          day: '日视图',
        },
        initialView: 'resourceTimeGridDay',
        initialDate: moment().format('YYYY-MM-DD'), // 设置初始日期为今天
        timeZone: 'local', // 使用本地时区，而不是UTC
        aspectRatio: 1.5,
        editable: true,
        selectable: true,
        selectMirror: true,
        dayMaxEvents: true,
        eventStartEditable: true,
        eventDurationEditable: true,
        droppable: true,
        nowIndicator: true,
        slotEventOverlap: false,
        allDaySlot: false,
        slotDuration: '00:30:00',
        // 设置日历显示的时间范围
        slotMinTime: '07:00:00', // 开始时间：早上7点
        slotMaxTime: '23:59:00', // 结束时间：晚上23:59
        select: this.handleDateSelect,
        eventClick: this.handleEventClick,
        eventDrop: this.handleEventDrop,
        eventResize: this.handleEventResize,
        datesSet: this.handleDatesSet,
        resourceAreaColumns: [
          {
            group: true,
            field: 'building',
            headerContent: '区域',
          },
          {
            field: 'title',
            headerContent: '会议室',
          },
          {
            field: 'occupancy',
            headerContent: '会议室容量',
          },
        ],
        resources: [], // 初始化为空数组，将通过 API 获取数据后更新
        events: [
          // 初始事件数据
          //  { resourceId: '1', title: '会议 3', start: '2025-05-13 12:00:00', end: '2025-05-13 16:00:00' },
        ],

          // { resourceId: 'a', title: '会议 3', start: '2025-05-13T12:00:00+00:00', end: '2025-05-1316:00:00+00:00' },
          // { resourceId: 'b', title: '会议 4', start: '2025-05-13T07:30:00+00:00', end: '2025-05-13T09:30:00+00:00' },
          // { resourceId: 'b', title: '会议 5', start: '2025-05-13T10:00:00+00:00', end: '2025-05-13T15:00:00+00:00' },
          // { resourceId: 'c', title: '会议 2', start: '2025-05-13T09:00:00+00:00', end: '2025-05-13T14:00:00+00:00' },
          // { resourceId: 'd', title: '会议 6', start: '2025-05-13T15:30:00+00:00', end: '2025-05-13T17:30:00+00:00' },
          // { resourceId: 'e', title: '会议 7', start: '2025-05-13T17:00:00+00:00', end: '2025-05-13T19:00:00+00:00' },
          // { resourceId: 'f', title: '会议 8', start: '2025-05-13T14:00:00+00:00', end: '2025-05-13T16:00:00+00:00' },
      },
      lastValidEvent: null, // 存储事件的上一个有效状态
    }
  },
  methods: {
    // 检查事件是否可编辑，并返回适当的错误消息
    checkEventEditability(eventStart, eventEnd) {
      const now = new Date();
      const eventStartTime = new Date(eventStart);
      const eventEndTime = new Date(eventEnd);
      const fiveMinutesBeforeStart = new Date(eventStartTime.getTime() - 5 * 60 * 1000);
      
      // 情况1: 当前时间在开始时间前5分钟以内
      if (now > fiveMinutesBeforeStart && now < eventStartTime) {
        return {
          editable: false,
          message: '5分钟内开始的会议无法修改'
        };
      }
      
      // 情况2: 当前时间在开始时间和结束时间之间（会议正在进行）
      if (now >= eventStartTime && now <= eventEndTime) {
        return {
          editable: false,
          message: '正在进行的会议无法修改'
        };
      }
      
      // 情况3: 当前时间晚于结束时间（会议已结束）
      if (now > eventEndTime) {
        return {
          editable: false,
          message: '已经结束的会议无法编辑'
        };
      }
      
      // 可以编辑
      return {
        editable: true,
        message: ''
      };
    },
    
    // 处理日期选择（创建新事件）
    handleDateSelect(selectInfo) {
      console.log('Date selected:', selectInfo);
      console.log('当前日期:', this.showDay);
      console.log('选择的开始时间:', selectInfo.startStr);
      console.log('选择的结束时间:', selectInfo.endStr);
      
      // 检查选择的开始时间是否在过去
      const now = new Date();
      const selectedStart = new Date(selectInfo.startStr);
      
      // 添加5分钟的缓冲时间，避免因为时间精度问题导致的误判
      const fiveMinutesAgo = new Date(now.getTime() - 5 * 60 * 1000);
      
      console.log('当前时间:', now);
      console.log('选择时间:', selectedStart);
      console.log('5分钟前:', fiveMinutesAgo);
      
      if (selectedStart < fiveMinutesAgo) {
        this.$message({
          message: '不允许新建时间过去的会议',
          type: 'warning'
        });
        return; // 阻止创建
      }
      
      // 获取选中的资源（会议室）
      let resourceId = '';
      if (selectInfo.resource && selectInfo.resource.id) {
        resourceId = selectInfo.resource.id;
      } else {
        resourceId = this.getFirstResourceId();
        // 如果没有可用的资源ID，显示提示并返回
        if (!resourceId) {
          this.$message({
            message: '请先选择一个会议室',
            type: 'warning'
          });
          return;
        }
      }
      
      const resourceName = this.getResourceNameById(resourceId);
      
      // 检查是否与现有事件冲突
      const { hasConflict, conflictEvent } = this.checkTimeConflict(
        selectInfo.startStr,
        selectInfo.endStr,
        resourceId
      );
      
      if (hasConflict) {
        // 显示冲突警告但仍然允许用户尝试创建（可能会调整时间）
        this.$message({
          message: `注意：该会议室在所选时间段已有预订（${conflictEvent.title}）`,
          type: 'warning'
        });
      }
      
      this.isEditMode = false;
      this.currentEvent = {
        start: selectInfo.startStr,
        end: selectInfo.endStr,
        resourceId: resourceId,
        allDay: selectInfo.allDay,
        id: selectInfo.id,
        extendedProps: {
          resourceName: resourceName,
          userId: userId.value,
          username: username.value,
          departmentName: departmentName.value,
          departmentId: departmentId.value,
          orgId: orgId.value,
          orgName: orgName.value,  
        }
      };
      
      console.log('创建新事件:', this.currentEvent);
      this.showDrawer = true;
    },
    
    // 获取第一个可用的资源 ID
    getFirstResourceId() {
      if (this.roomlist && this.roomlist.length > 0) {
        return this.roomlist[0].id.toString();
      }
      
      // 如果没有会议室列表，尝试从日历资源中获取
      const calendarApi = this.$refs.fullCalendar?.getApi();
      if (calendarApi) {
        const resources = calendarApi.getResources();
        if (resources && resources.length > 0) {
          return resources[0].id;
        }
      }
      
      console.warn('没有找到可用的会议室资源');
      return ''; // 返回空字符串，调用方需要检查
    },
    
    async fetchSpaceData() {
      this.treeLoading = true
      const { data } = await getTreeByFloor()
      this.spacedata = data.floorTree
      this.treeLoading = false
    },
    
    async fetchData() {
      this.listLoading = true
      const { data } = await getMeetingList(this.queryForm)
      this.meetingdata = data.list
      this.total = data.total
      
      // 转换会议数据为 FullCalendar 事件格式
      this.convertMeetingDataToEvents(data.list)
      
      await this.fetchMeetingRoomData()

      // await this.fetchMeetingList()

      this.listLoading = false
    },
    async fetchMeetingList() {
      const { data } = await getMList({day:'2025-06-08'})
      this.getListObj = data.list
      console.log('获取到的会议列表:', this.getListObj)
    },

    async saveSchedule(data) {
      const { msg } = await saveSchedule(data)
      console.log("saveSchedule",saveSchedule);
      // await $baseMessage(msg, 'success', 'hey')
      await this.fetchData()
    },
    
    async fetchMeetingRoomData() {
      const { data } = await getMRoomList(this.queryForm)
      this.roomlist = data.list
      console.log('获取到的会议室列表:', this.roomlist)
      
      // 更新 FullCalendar 的 resources
      this.updateCalendarResources()
    },
    
    updateCalendarResources() {
      if (!this.roomlist || this.roomlist.length === 0) {
        console.log('会议室列表为空，不更新资源')
        // return
      }
      
      // 将 roomlist 转换为 FullCalendar 需要的 resources 格式
      const resources = this.roomlist.map(room => ({
        id: room.id.toString(), // 确保 ID 是字符串类型
        building: this.queryForm.floorCode || '未知楼层', // 使用当前选中的楼层
        title: room.name || '未命名会议室',
        occupancy: room.occupancy || 0, // 如果没有容量信息，默认为 0
        code: room.code // 保存原始代码，可能在其他地方需要
      }))
      
      console.log('更新日历资源为:', resources)
      
      // 更新 FullCalendar 的 resources
      const calendarApi = this.$refs.fullCalendar?.getApi()
      if (calendarApi) {
        // 移除所有现有资源
        const currentResources = calendarApi.getResources()
        currentResources.forEach(resource => resource.remove())
        
        // 添加新资源
        resources.forEach(resource => {
          calendarApi.addResource(resource)
        })
        
        console.log('日历资源已更新')
      } else {
        // 如果日历 API 尚未初始化，直接更新选项
        this.calendarOptions.resources = resources
        console.log('日历尚未初始化，直接更新资源选项')
      }
    },
    
    // 处理事件点击（编辑现有事件）
    handleEventClick(clickInfo) {
      console.log('Event clicked:', clickInfo.event);
      
      // 检查当前用户是否是会议预订者
      const currentUserId = userId.value.toString();
      const eventBookerId = clickInfo.event.extendedProps?.booker?.toString() || '';
      
      if (currentUserId !== eventBookerId) {
        this.$message({
          message: '无法编辑他人的会议日程',
          type: 'warning'
        });
        return; // 阻止编辑
      }
      
      // 检查事件是否可编辑
      const { editable, message } = this.checkEventEditability(
        clickInfo.event.start,
        clickInfo.event.end
      );
      
      if (!editable) {
        this.$message({
          message: message,
          type: 'warning'
        });
        return; // 阻止编辑
      }
      
      // 获取事件关联的资源（会议室）
      const resource = clickInfo.event.getResources()[0];
      const resourceId = resource ? resource.id : '';
      const resourceName = resource ? resource.title : '';
      
      this.isEditMode = true;
      this.currentEvent = {
        id: clickInfo.event.id,
        title: clickInfo.event.title,
        start: clickInfo.event.startStr,
        end: clickInfo.event.endStr,
        resourceId: resourceId,
        backgroundColor: clickInfo.event.backgroundColor,
        extendedProps: {
          ...clickInfo.event.extendedProps,
          resourceName: resourceName,
          userId: userId.value,
          username: username.value,
          departmentName: departmentName.value,
          departmentId: departmentId.value,
          orgId: orgId.value,
          orgName: orgName.value,  
        }
      };
      
      console.log('编辑事件:', this.currentEvent);
      this.showDrawer = true;
    },
    
    // 处理事件拖动
    handleEventDrop(eventDropInfo) {
      console.log('Event dropped:', eventDropInfo.event.title);
      
      const event = eventDropInfo.event;
      
      // 检查当前用户是否是会议预订者
      const currentUserId = userId.value.toString();
      const eventBookerId = event.extendedProps?.booker?.toString() || '';
      
      if (currentUserId !== eventBookerId) {
        this.$message({
          message: '无法编辑他人的会议日程',
          type: 'warning'
        });
        eventDropInfo.revert(); // 恢复事件到原始位置
        return; // 阻止编辑
      }
      
      // 检查事件是否可编辑
      const { editable, message } = this.checkEventEditability(
        event.start,
        event.end
      );
      
      if (!editable) {
        this.$message({
          message: message,
          type: 'warning'
        });
        eventDropInfo.revert(); // 恢复事件到原始位置
        return;
      }
      
      const resourceId = event.getResources()[0]?.id || '';
      
      // 检查时间冲突
      const { hasConflict, conflictEvent } = this.checkTimeConflict(
        event.startStr,
        event.endStr,
        resourceId,
        event.id
      );
      
      if (hasConflict) {
        // 有冲突，恢复到原始状态
        this.$message({
          message: `时间冲突：该会议室在所选时间段已被预订（${conflictEvent.title}）`,
          type: 'warning'
        });
        
        // 恢复事件到拖动前的状态
        eventDropInfo.revert();
      } else {
        // 无冲突，打开编辑抽屉
        this.openEditDrawerForEvent(event);
      }
    },
    
    // 处理事件调整大小
    handleEventResize(eventResizeInfo) {
      console.log('Event resized:', eventResizeInfo.event.title);
      
      const event = eventResizeInfo.event;
      
      // 检查当前用户是否是会议预订者
      const currentUserId = userId.value.toString();
      const eventBookerId = event.extendedProps?.booker?.toString() || '';
      
      if (currentUserId !== eventBookerId) {
        this.$message({
          message: '无法编辑他人的会议日程',
          type: 'warning'
        });
        eventResizeInfo.revert(); // 恢复事件到原始大小
        return; // 阻止编辑
      }
      
      // 检查事件是否可编辑
      const { editable, message } = this.checkEventEditability(
        event.start,
        event.end
      );
      
      if (!editable) {
        this.$message({
          message: message,
          type: 'warning'
        });
        eventResizeInfo.revert(); // 恢复事件到原始大小
        return;
      }
      
      const resourceId = event.getResources()[0]?.id || '';
      
      // 检查时间冲突
      const { hasConflict, conflictEvent } = this.checkTimeConflict(
        event.startStr,
        event.endStr,
        resourceId,
        event.id
      );
      
      if (hasConflict) {
        // 有冲突，恢复到原始状态
        this.$message({
          message: `时间冲突：该会议室在所选时间段已被预订（${conflictEvent.title}）`,
          type: 'warning'
        });
        
        // 恢复事件到调整前的状态
        eventResizeInfo.revert();
      } else {
        // 无冲突，打开编辑抽屉
        console.log('无冲突，打开编辑抽屉',event);
        this.openEditDrawerForEvent(event);
      }
    },
    
    // 打开编辑抽屉的通用方法
    openEditDrawerForEvent(event) {
      // 获取事件关联的资源（会议室）
      const resource = event.getResources()[0];
      const resourceId = resource ? resource.id : '';
      const resourceName = resource ? resource.title : '';
      
      this.isEditMode = true;
      this.currentEvent = {
        id: event.id,
        title: event.title,
        start: event.startStr,
        end: event.endStr,
        resourceId: resourceId,
        backgroundColor: event.backgroundColor,
        extendedProps: {
          ...event.extendedProps,
          resourceName: resourceName,
          userId: userId.value,
          username: username.value,
          departmentName: departmentName.value,
          departmentId: departmentId.value,
          orgId: orgId.value,
          orgName: orgName.value,  
        }
      };
      
      console.log('编辑事件:', this.currentEvent);
      this.showDrawer = true;
    },
    
    // 处理事件接收（从一个资源拖到另一个资源）
    handleEventReceive(info) {
      const event = info.event;
      const resourceId = event.getResources()[0]?.id || '';
      
      // 检查时间冲突
      const { hasConflict, conflictEvent } = this.checkTimeConflict(
        event.startStr,
        event.endStr,
        resourceId,
        event.id
      );
      
      if (hasConflict) {
        // 有冲突，移除新添加的事件
        this.$message({
          message: `时间冲突：该会议室在所选时间段已被预订（${conflictEvent.title}）`,
          type: 'warning'
        });
        
        // 移除事件
        event.remove();
      } else {
        // 无冲突，打开编辑抽屉
        this.openEditDrawerForEvent(event);
      }
    },
    
    // 更新日历配置，添加事件拖动和调整大小的处理
    updateCalendarConfig() {
      // 更新日历配置
      this.calendarOptions = {
        ...this.calendarOptions,
        eventDrop: this.handleEventDrop,
        eventResize: this.handleEventResize,
        eventReceive: this.handleEventReceive,
        // 确保拖动和调整大小是启用的
        editable: true,
        eventStartEditable: true,
        eventResizableFromStart: false, // 只允许从结束时间调整大小
        eventDurationEditable: true,
        droppable: true,
      };
    },
    
    // 在组件创建时调用此方法
    created() {
      this.updateCalendarConfig();
    },
    handleNodeClick(treenode) {
      this.queryForm.spaceCode = ''
      this.queryForm.floorAreaCode = ''
      this.queryForm.floorCode = ''
      this.queryForm.areaCode = ''
      this.queryForm.areaType = ''
      
      if (treenode.spaceCode) {
        this.queryForm.spaceCode = treenode.spaceCode
      }
      if (treenode.floorAreaCode) {
        this.queryForm.floorAreaCode = treenode.floorAreaCode
      }
      if (treenode.floorCode) {
        this.queryForm.floorCode = treenode.floorCode
        //crumblist.value = treenode.crumblist
      }
      if (treenode.areaCode) {
        this.queryForm.areaCode = treenode.areaCode
      }
      if (treenode.areaType) {
        this.queryForm.areaType = treenode.areaType
      }
      
      if (treenode.floorCode || treenode.areaCode) {
        this.fetchData() // 获取会议室数据并更新日历资源
      }
    },
    handleFormSubmit(formData, apiData) {
      // 确保有日期部分
      const ensureFullDateTime = (timeStr, formdata) => {
        if (!timeStr) return null;
        return formdata.selectDay + ' ' + timeStr;
      };
      
      const startTime = ensureFullDateTime(formData.startTime, formData);
      const endTime = ensureFullDateTime(formData.endTime, formData);
      const resourceId = formData.resourceId;
      
      // 检查开始时间是否在过去
      const now = new Date();
      const startDateTime = new Date(startTime);
      const endDateTime = new Date(endTime);
      
      if (!this.isEditMode) {
        // 新建事件检查
        if (startDateTime <= now) {
          this.$message({
            message: '不允许新建时间在过去的会议',
            type: 'warning'
          });
          return; // 阻止提交
        }
      } else {
        // 编辑事件检查
        const { editable, message } = this.checkEventEditability(
          startDateTime,
          endDateTime
        );
        
        if (!editable) {
          this.$message({
            message: message,
            type: 'warning'
          });
          return; // 阻止提交
        }
      }
      
      // 检查时间冲突
      const { hasConflict, conflictEvent } = this.checkTimeConflict(
        startTime, 
        endTime, 
        resourceId,
        this.isEditMode ? formData.id : null
      );
      
      if (hasConflict) {
        // 显示冲突警告
        this.$message({
          message: `时间冲突：该会议室在所选时间段已被预订（${conflictEvent.title}）`,
          type: 'warning'
        });
        return; // 阻止提交
      }
      
      // 无冲突，继续处理表单提交
      const calendarApi = this.$refs.fullCalendar.getApi();
      
      if (this.isEditMode && formData.id) {
        // 更新现有事件
        // ... 现有的更新事件代码 ...
      } else {
        // 添加新事件
        // ... 现有的添加事件代码 ...
      }
      
      console.log('提交表单数据:', apiData);
      this.saveSchedule(apiData);
      this.resetForm();
    },
    
    resetForm() {
      this.showDrawer = false;
      this.currentEvent = {};
      this.isEditMode = false;
    },

    // 处理日历日期变化
    handleDatesSet(dateInfo) {
      // 当日历视图日期变化时，更新 showDay
      const newDate = moment(dateInfo.start).format('YYYY-MM-DD');
      
      // 只有当日期真正改变时才重新获取数据，避免无限循环
      if (this.showDay !== newDate) {
        this.showDay = newDate;
        console.log('日历日期已更新为:', this.showDay);
        
        // 重新获取新日期的会议数据
        if (this.queryForm.floorCode || this.queryForm.areaCode) {
          this.fetchData();
        }
      }
    },
    // 手动更新日历日期
    updateCalendarDate() {
      const calendarApi = this.$refs.fullCalendar.getApi();
      calendarApi.gotoDate(this.showDay);
      console.log('手动设置日历日期为:', this.showDay);
      
      // 重新获取选中日期的会议数据
      if (this.queryForm.floorCode || this.queryForm.areaCode) {
        this.fetchData();
      }
      
      // 重新初始化日历设置
      this.initCalendarSettings();
    },
    // 根据资源ID获取资源名称
    getResourceNameById(resourceId) {
      if (!resourceId || !this.roomlist || this.roomlist.length === 0) {
        return '';
      }
      
      const resource = this.roomlist.find(room => room.id.toString() === resourceId.toString());
      return resource ? resource.name : '';
    },
    
    // 将会议室数据转换为 FullCalendar 事件
    convertMeetingDataToEvents(meetingRooms) {
      console.log('会议室数据:', meetingRooms)
      if (!meetingRooms || meetingRooms.length === 0) {
        console.log('没有会议室数据，不更新事件')
        return
      }
      
      // 获取日历 API
      const calendarApi = this.$refs.fullCalendar?.getApi()
      if (!calendarApi) {
        console.log('日历 API 未初始化，无法更新事件')
        return
      }
      
      // 移除所有现有事件
      calendarApi.removeAllEvents()
      
      // 创建新事件数组
      const events = []
      
      // 遍历所有会议室及其日程
      meetingRooms.forEach(room => {
        const roomId = room.meetingRoomId.toString()
        
        // 检查会议室是否有日程安排
        if (room.schedule && room.schedule.length > 0) {
          // 遍历会议室的所有日程



          room.schedule.forEach(schedule => {

            //将数字时间转换回来
            let startTime = schedule.startTime
            let endTime = schedule.endTime
            console.log('开始时间:', startTime)
            console.log('结束时间:', endTime)
            startTime = moment.unix(startTime).format("YYYY-MM-DD HH:mm")
            endTime = moment.unix(endTime).format("YYYY-MM-DD HH:mm")
            // startTime = moment(startTime).format('YYYY-MM-DD HH:mm')
            // endTime =  moment(endTime).format('YYYY-MM-DD HH:mm')

            console.log('开始时间:', startTime)
            console.log('结束时间:', endTime)
            // 创建事件对象
            const event = {
              id: schedule.bookingId,
              resourceId: roomId,
              title: schedule.meetingSubject || '未命名会议',
              start: startTime,
              end: endTime,
              backgroundColor: this.getStatusColor(schedule.status),
              extendedProps: {
                description: schedule.meetingSubject,
                resourceName: room.meetingRoomName,
                booker: schedule.booker,
                bookerName: schedule.bookerName,
                bookerDept: schedule.bookerDept,
                status: schedule.status,
                bookingId: schedule.bookingId,
                scheduleId: schedule.scheduleId
              }
            }
            
            // 添加到事件数组
            events.push(event)
          })
        }
      })
      
      // 将事件添加到日历
      events.forEach(event => {
        calendarApi.addEvent(event)
      })
      console.log("events",events)
      console.log(`已将 ${events.length} 个会议转换为日历事件`)
    },
    
    // 根据会议状态获取颜色
    getStatusColor(status) {
      // 可以根据不同的状态返回不同的颜色
      const statusColors = {
        '0': '#4D7CFE', // 已预订
        '1': '#FF6B6B', // 已取消
        '2': '#FFA500', // 进行中
        '3': '#28a745'  // 已完成
      }
      
      return statusColors[status] || '#4D7CFE' // 默认颜色
    },
    // 检查时间冲突
    checkTimeConflict(startTime, endTime, resourceId, eventId = null) {
      const calendarApi = this.$refs.fullCalendar.getApi();
      if (!calendarApi) {
        console.error('日历API未初始化');
        return { hasConflict: false };
      }
      
      const events = calendarApi.getEvents();
      
      // 过滤出同一资源（会议室）的事件
      const resourceEvents = events.filter(event => {
        // 如果是编辑现有事件，排除自身
        if (eventId && event.id === eventId) {
          return false;
        }
        
        // 检查是否是同一资源
        const eventResources = event.getResources();
        // 添加安全检查，确保资源存在且有id属性
        return eventResources && eventResources.length > 0 && 
               eventResources.some(resource => resource && resource.id === resourceId);
      });
      
      // 将字符串时间转换为 Date 对象
      const newStart = new Date(startTime);
      const newEnd = new Date(endTime);
      
      // 检查是否与现有事件冲突
      for (const event of resourceEvents) {
        const existingStart = event.start;
        const existingEnd = event.end;
        
        // 确保开始和结束时间存在
        if (!existingStart || !existingEnd) {
          continue;
        }
        
        // 检查时间重叠
        if (
          (newStart >= existingStart && newStart < existingEnd) ||
          (newEnd > existingStart && newEnd <= existingEnd) ||
          (newStart <= existingStart && newEnd >= existingEnd)
        ) {
          return {
            hasConflict: true,
            conflictEvent: event
          };
        }
      }
      
      return { hasConflict: false };
    },
  },
  // 将mounted中的逻辑封装为单独的方法
  initCalendarSettings() {
    // 初始化日历后，设置事件可编辑性
    this.$nextTick(() => {
      const calendarApi = this.$refs.fullCalendar?.getApi();
      if (calendarApi) {
        // 设置事件渲染器，根据开始时间和结束时间动态设置事件是否可编辑
        this.calendarOptions.eventDidMount = (info) => {
          const now = new Date();
          const eventStartTime = new Date(info.event.start);
          const eventEndTime = new Date(info.event.end);
          const fiveMinutesBeforeStart = new Date(eventStartTime.getTime() - 5 * 60 * 1000);
          
          let isEditable = true;
          
          // 检查当前用户是否是会议预订者
          const currentUserId = userId.value.toString();
          const eventBookerId = info.event.extendedProps?.booker?.toString() || '';
          console.log('当前用户ID:', currentUserId);
          console.log('会议预订者ID:', info.event.extendedProps);
          if (currentUserId !== eventBookerId) {
            isEditable = false;
          }
          
          // 情况1: 当前时间在开始时间前5分钟以内
          if (now > fiveMinutesBeforeStart && now < eventStartTime) {
            isEditable = false;
          }
          
          // 情况2: 当前时间在开始时间和结束时间之间（会议正在进行）
          if (now >= eventStartTime && now <= eventEndTime) {
            isEditable = false;
          }
          
          // 情况3: 当前时间晚于结束时间（会议已结束）
          if (now > eventEndTime) {
            isEditable = false;
          }
          
          if (!isEditable) {
            // 添加视觉提示（灰色或半透明）
            info.el.style.opacity = '0.7';
            info.el.style.cursor = 'not-allowed';
            
            // 禁用拖动和调整大小
            info.event.setProp('editable', false);
          }
        };
      }
    });
  },
  mounted() {
    this.fetchSpaceData().then(() => {
      // 初始化完成后，可以选择默认加载第一个楼层的会议室
      if (this.spacedata && this.spacedata.length > 0) {
        // 找到第一个有 floorCode 的节点
        const findFirstFloorNode = (nodes) => {
          for (const node of nodes) {
            if (node.floorCode) {
              return node;
            }
            if (node.children && node.children.length > 0) {
              const found = findFirstFloorNode(node.children);
              if (found) return found;
            }
          }
          return null;
        };
        
        const firstFloorNode = findFirstFloorNode(this.spacedata);
        if (firstFloorNode) {
          console.log('自动选择第一个楼层:', firstFloorNode);
          this.handleNodeClick(firstFloorNode);
        }
      }
    });
    
    console.log('Calendar mounted with options:', this.calendarOptions);
    
    // 调用初始化日历设置方法
    this.initCalendarSettings();
  }
})
</script>

<style lang="css">
/* 保留原有样式 */
h2 {
  margin: 0;
  font-size: 16px;
}

/* ... 其他原有样式 ... */

/* 添加日历高度相关样式 */
.meetingroom-container {
  height: calc(100vh - 120px);
  overflow: hidden;
}

.auto-height-card1 {
  height: calc(100vh - 150px);
  overflow: auto;
}

.fc {
  /* the calendar root */
  margin: 0 auto;
  height: 100% !important;
}

.fc-view-harness {
  height: calc(100vh - 250px) !important;
  min-height: 500px;
}

.fc-timegrid-body {
  height: 100% !important;
  overflow-y: auto;
}

.el-card {
  height: calc(100vh - 150px);
  overflow: hidden;
}

.demo-app-calendar {
  height: 100%;
}
</style>
<template>
  <el-drawer
    v-model="visible"
    :title="isEdit ? `编辑会议(${form.selectDay})` : `新增会议(${form.selectDay})`"
    direction="rtl"
    size="30%"
    :before-close="handleClose"
  >
    <el-form ref="formRef" :model="form" label-width="100px" :rules="rules">
      <el-form-item label="会议室" prop="resourceName">
        <span style="font-size:20px">{{form.resourceName}}</span>
        <el-input v-model="form.resourceName" style="display:none" />
        <el-input v-model="form.resourceId" style="display:none" />
      </el-form-item>
      <el-form-item label="会议名称" prop="title">
        <el-input v-model="form.title" placeholder="请输入会议名称" />
      </el-form-item>
      
      <el-form-item label="开始时间" prop="startTime">
        <el-time-picker
          v-model="form.startTime"
          placeholder="开始时间"
          format="HH:mm:ss"
          value-format="HH:mm:ss"
          @change="updateEndTime"
        />
      </el-form-item>
      
      <el-form-item label="结束时间" prop="endTime">
        <el-time-picker
          v-model="form.endTime"
          placeholder="结束时间"
          format="HH:mm:ss"
          value-format="HH:mm:ss"
        />
      </el-form-item>
      
      <el-form-item label="会议描述">
        <el-input
          v-model="form.description"
          type="textarea"
          placeholder="请输入会议描述"
        />
      </el-form-item>
      
      <el-form-item label="标记颜色">
        <el-color-picker v-model="form.color" show-alpha />
      </el-form-item>

    </el-form>
    
    <template #footer>
      <div style="flex: auto">
        <el-button type="danger" @click="handleDelete">删除</el-button>
        <el-button type="primary" @click="submitForm">确认</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script>
import { defineComponent, ref, reactive, watch, computed } from 'vue'
import moment from 'moment/moment'
import { deleteSchedule } from '/@/api/sence.ts'
import { ElMessageBox } from 'element-plus'
import { start } from 'nprogress'

export default defineComponent({
  name: 'MeetingForm',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    eventData: {
      type: Object,
      default: () => ({})
    },
    isEdit: {
      type: Boolean,
      default: false
    },
    resources: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:modelValue', 'submit', 'close'],
  setup(props, { emit }) {
    const formRef = ref(null)
    const visible = ref(props.modelValue)

    const form = reactive({
      id: '',
      title: '',
      startTime: '',
      endTime: '',
      description: '',
      color: '#4D7CFE',
      resourceId: '',
      resourceName: '', // 存储会议室名称
      // 保存原始日期时间，用于提交时恢复
      originalStart: '',
      originalEnd: ''
    })
    
    const rules = {
            

      title: [{ required: true, message: '请输入会议名称', trigger: 'blur' }],
      startTime: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
      endTime: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
      resourceId: [{ required: true, message: '请选择会议室', trigger: 'change' }],
      resourceName: [{ required: true, trigger: 'blur' }],
    }
    
    // 从完整的日期时间字符串中提取时间部分 (HH:mm:ss)，并处理时区问题
    const extractTimeFromDateTime = (dateTimeStr) => {
      if (!dateTimeStr) return ''
      // moment.tz.setDefault('Asia/Shanghai')
      return moment(dateTimeStr).format('HH:mm:ss')
      // try {
      //   // 尝试创建日期对象
      //   const date = new Date(dateTimeStr)
        
      //   // 检查日期是否有效
      //   if (isNaN(date.getTime())) {
      //     console.error('Invalid date:', dateTimeStr)
      //     return ''
      //   }
        
      //   // 获取本地时间（处理时区问题）
      //   const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000)
        
      //   // 格式化为 HH:mm:ss
      //   const hours = localDate.getHours().toString().padStart(2, '0')
      //   const minutes = localDate.getMinutes().toString().padStart(2, '0')
      //   const seconds = localDate.getSeconds().toString().padStart(2, '0')
        
      //   console.log(`转换时间: ${dateTimeStr} -> ${hours}:${minutes}:${seconds}`)
      //   return `${hours}:${minutes}:${seconds}`
      // } catch (error) {
      //   console.error('Error extracting time:', error)
      //   return ''
      // }
    }
    
    // 更新结束时间
    const updateEndTime = () => {
      if (form.startTime && !form.endTime) {
        // // 解析开始时间
        // const [hours, minutes, seconds] = form.startTime.split(':').map(Number)
        
        // // 创建一个临时日期对象
        // const tempDate = new Date()
        // tempDate.setHours(hours, minutes, seconds, 0)
        
        // // 添加一小时
        // tempDate.setHours(tempDate.getHours() + 1)
        
        // // 格式化为 HH:mm:ss
        // const endHours = tempDate.getHours().toString().padStart(2, '0')
        // const endMinutes = tempDate.getMinutes().toString().padStart(2, '0')
        // const endSeconds = tempDate.getSeconds().toString().padStart(2, '0')
        
        // form.endTime = `${endHours}:${endMinutes}:${endSeconds}`
        form.endTime = moment(form.startTime).add(1, 'hours').format('HH:mm:ss')
      }
    }
    
    // 更新会议室名称
    const updateResourceName = () => {
      if (form.resourceId) {
        const selectedResource = props.resources.find(r => r.id === form.resourceId)
        if (selectedResource) {
          form.resourceName = selectedResource.title
          console.log(`更新会议室名称: ${form.resourceName} (ID: ${form.resourceId})`)
        }
      } else {
        form.resourceName = ''
      }
    }
    
    const handleClose = () => {
      emit('update:modelValue', false)
      emit('close')
    }
    
    const submitForm = () => {
      formRef.value.validate((valid) => {
        if (valid) {
          // 准备提交的数据
          const formData = { ...form }
          
          // // 恢复原始日期，但使用表单中选择的时间
          // if (form.originalStart && form.startTime) {
          //   const originalDate = new Date(form.originalStart)
          //   const [hours, minutes, seconds] = form.startTime.split(':').map(Number)
            
          //   // 设置本地时间
          //   originalDate.setHours(hours, minutes, seconds, 0)
          //   formData.startTime = originalDate.toISOString()
          // }
          
          // if (form.originalEnd && form.endTime) {
          //   const originalDate = new Date(form.originalEnd)
          //   const [hours, minutes, seconds] = form.endTime.split(':').map(Number)
            
          //   // 设置本地时间
          //   originalDate.setHours(hours, minutes, seconds, 0)
          //   formData.endTime = originalDate.toISOString()
          // }
          
          // 删除辅助字段，不需要提交
          // delete formData.originalStart
          // delete formData.originalEnd
          //将时间转换为数字
          let startTime = formData.selectDay + ' ' + formData.startTime
          let endTime = formData.selectDay + ' ' + formData.endTime

          // startTime = new Date(startTime).getTime()
          // endTime = new Date(endTime).getTime()
          startTime = moment(startTime).unix()
          endTime = moment(endTime).unix()
          console.log('开始时间:', startTime)
          console.log('结束时间:', endTime)
          const apiData = [{
              "meetingRoomId": formData.resourceId,
              "meetingRoomName": formData.resourceName,
              "capacity": 12, // 默认值，可以从资源中获取
              "schedule": [
                {
                  "startTime": startTime,
                  "endTime": endTime,
                  "status": "0",
                  "booker": form.userId, // 默认值，可以从用户信息中获取
                  "bookingId": formData.id || "0",
                  "scheduleId": formData.id || "0",
                  "meetingSubject": formData.title,
                  "bookerDept": form.orgName + '/' + form.departmentName, // 默认值，可以从用户信息中获取
                  "bookerName": form.username // 默认值，可以从用户信息中获取
                }
              ]
            }]
            console.log('提交表单数据:', apiData)
          emit('submit', formData,apiData)
          handleClose()
        }
      })
    }
    
    const handleDelete = () => {
      // 只有在编辑模式下才能删除
      if (!props.isEdit || !form.id) {
        handleClose()
        return
      }
      
      ElMessageBox.confirm(
        '确定要删除此会议吗？此操作不可恢复。',
        '删除确认',
        {
          confirmButtonText: '确定删除',
          cancelButtonText: '取消',
          type: 'warning',
        }
      )
        .then(async () => {
          try {
            console.log(form.id)
            await deleteSchedule({ bookingId: form.id })
            // 通知父组件刷新日历
            emit('fetach', { deleted: true, id: form.id })
            handleClose()
          } catch (error) {
            console.error('删除会议失败:', error)
          }
        })
        .catch(() => {
          // 用户取消删除，不做任何操作
        })
    }
    
    // Watch for changes in props
    watch(
      () => props.modelValue,
      (newVal) => {
        visible.value = newVal
      }
    )
    
    watch(
      () => props.eventData,
      (newVal) => {
        if (newVal && Object.keys(newVal).length > 0) {
          console.log('接收到事件数据:', newVal)
          
          // 保存原始日期时间
          form.originalStart = newVal.start || ''
          form.originalEnd = newVal.end || ''
          form.userId = newVal.extendedProps?.userId || ''
          form.username = newVal.extendedProps?.username || ''
          form.departmentName = newVal.extendedProps?.departmentName || ''
          form.departmentId = newVal.extendedProps?.departmentId || ''
          form.orgId = newVal.extendedProps?.orgId || ''
          form.orgName = newVal.extendedProps?.orgName || ''
          form.id = newVal.id || ''
          form.title = newVal.title || form.username + '预定的会议'
          form.startTime = extractTimeFromDateTime(newVal.start) || ''
          form.endTime = extractTimeFromDateTime(newVal.end) || ''
          form.description = newVal.extendedProps?.description || ''
          form.color = newVal.backgroundColor || '#4D7CFE'
          form.resourceId = newVal.resourceId || ''
          form.selectDay = moment(newVal.start).format('YYYY-MM-DD')


          // 如果事件数据中包含resourceName，直接使用
          if (newVal.extendedProps?.resourceName) {
            form.resourceName = newVal.extendedProps.resourceName
            console.log(`使用事件中的会议室名称: ${form.resourceName}`)
          } else {
            // 否则根据resourceId查找
            updateResourceName()
          }
          
          console.log('事件数据已加载:', {
            original: {
              start: newVal.start,
              end: newVal.end
            },
            formatted: {
              startTime: form.startTime,
              endTime: form.endTime,
              resourceId: form.resourceId,
              resourceName: form.resourceName
            }
          })
        } else {
          // Reset form for new event
          const now = new Date()
          const oneHourLater = new Date(now.getTime() + 60 * 60 * 1000)
          
          form.id = ''
          form.title = ''
          form.originalStart = now.toISOString()
          form.originalEnd = oneHourLater.toISOString()
          form.startTime = extractTimeFromDateTime(now) || ''
          form.endTime = extractTimeFromDateTime(oneHourLater) || ''
          form.description = ''
          form.color = '#4D7CFE'
          
          // 如果有可用的会议室，默认选择第一个
          if (props.resources && props.resources.length > 0) {
            form.resourceId = props.resources[0].id
            updateResourceName()
          } else {
            form.resourceId = ''
            form.resourceName = ''
          }
          
          console.log('新事件表单已初始化默认值')
        }
      },
      { immediate: true, deep: true }
    )
    
    watch(
      () => visible.value,
      (newVal) => {
        emit('update:modelValue', newVal)
      }
    )
    
    // 添加资源选择
    const resourceOptions = computed(() => {
      // 从父组件获取资源列表
      const resources = props.resources || []
      return resources.map(resource => ({
        label: `${resource.title} (${resource.building || '未知区域'})`,
        value: resource.id
      }))
    })
    
    // 监听资源列表变化
    watch(
      () => props.resources,
      (newResources) => {
        if (newResources && newResources.length > 0) {
          console.log('资源列表已更新:', newResources)
          
          // 如果当前没有选择会议室，则选择第一个
          if (!form.resourceId) {
            form.resourceId = newResources[0].id
            updateResourceName()
            console.log('设置默认会议室:', form.resourceId, form.resourceName)
          } 
          // 如果当前选择的会议室不在列表中，则选择第一个
          else {
            const resourceIds = newResources.map(r => r.id)
            if (!resourceIds.includes(form.resourceId)) {
              form.resourceId = resourceIds[0]
              updateResourceName()
              console.log('更新为第一个可用会议室:', form.resourceId, form.resourceName)
            }
          }
        }
      }
    )
    
    return {
      formRef,
      visible,
      form,
      rules,
      updateEndTime,
      updateResourceName,
      handleClose,
      submitForm,
      handleDelete,
      resourceOptions
    }
  }
})
</script>

<style scoped>
.selected-resource {
  margin-top: 5px;
  font-size: 12px;
  color: #606266;
}
</style>
<template>
  <vab-card :body-style="{ height: '210px' }" skeleton>
    <template #header>
      <vab-icon icon="align-top" />
      预定者排行
    </template>
    <vab-chart :option="option" />
  </vab-card>
</template>

<script lang="ts" setup>
import { useSettingsStore } from '/@/store/modules/settings'

const settingsStore = useSettingsStore()
const { color } = storeToRefs(settingsStore)
const option = reactive<any>({
  tooltip: {
    trigger: 'axis',
    extraCssText: 'z-index:1',
  },
  grid: {
    top: '0%',
    left: '2%',
    right: '20%',
    bottom: '0%',
    containLabel: true,
  },
  xAxis: [
    {
      splitLine: {
        show: false,
      },
      type: 'value',
      show: false,
    },
  ],
  yAxis: [
    {
      splitLine: {
        show: false,
      },
      axisLine: {
        show: false,
      },
      type: 'category',
      axisTick: {
        show: false,
      },
      data: ['曲丽丽', '付小小', '林东东', '周星星', '朱偏右'],
    },
  ],
  series: [
    {
      name: '累计消费',
      type: 'bar',
      barWidth: 15,
      label: {
        show: true,
        position: 'right',
        fontSize: 12,
        formatter: ({ data }: any) => {
          return `${data}`
        },
      },
      itemStyle: {
        borderRadius: 10,
        borderWidth: 2,
      },
      data: [23, 54, 68, 76, 87],
    },
  ],
})

watch(
  color,
  () => {
    option.color = [color.value]
  },
  { immediate: true }
)
</script>
<template>
  <vab-card :body-style="{ height: '210px' }" skeleton>
    <template #header>
      <vab-icon icon="line-chart-fill" />
      会议预定统计
    </template>
    <vab-chart :option="option" />
  </vab-card>
</template>

<script lang="ts" setup>
import { useSettingsStore } from '/@/store/modules/settings'
import { lightenColor } from '/@/utils/lightenColor'

const settingsStore = useSettingsStore()
const { color } = storeToRefs(settingsStore)
const option = reactive<any>({
  tooltip: {
    trigger: 'axis',
    extraCssText: 'z-index:1',
  },
  grid: {
    top: '4%',
    left: '2%',
    right: '2%',
    bottom: '0%',
    containLabel: true,
  },
  xAxis: [
    {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
      boundaryGap: false,
    },
  ],
  yAxis: [
    {
      type: 'value',
    },
  ],
  series: [
    {
      name: '预定量',
      type: 'line',
      data: [1295, 3020, 1330, 512, 4463, 2214, 3330, 2412, 1205, 820, 3330, 912],
      symbol: 'circle',
      smooth: true,
      yAxisIndex: 0,
      showSymbol: false,
      areaStyle: {
        opacity: 0.8,
      },
    },
  ],
})

watch(
  color,
  () => {
    option.color = [color.value, lightenColor(color.value, 50)]
  },
  { immediate: true }
)
</script>
<template>
  <div class="tabs">
    <vab-card class="tabs-card">
      <el-tabs v-model="activeName">
        <el-tab-pane label="会议预定记录" name="first">
          <el-table :data="tableData">
            <el-table-column label="日期" prop="date" />
            <el-table-column label="姓名" prop="name" />
            <el-table-column label="部门" prop="province" />
            <el-table-column label="类型" prop="city" />
            <el-table-column label="会议标题" prop="address" />
            <template #empty>
              <el-empty class="vab-data-empty" description="暂无数据" />
            </template>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="会议室配置" name="second">会议室配置</el-tab-pane>
        <el-tab-pane label="释放策略" name="thirty">释放策略配置</el-tab-pane>
        <el-tab-pane label="通知策略" name="four">通知策略</el-tab-pane>
        <el-tab-pane label="传感器配置" name="five">传感器配置</el-tab-pane>
        <el-tab-pane label="电子门牌" name="six">电子门牌</el-tab-pane>
        <el-tab-pane label="设施设备" name="seven">设施设备</el-tab-pane>
        <el-tab-pane label="中控配置" name="agant">中控配置</el-tab-pane>
        <el-tab-pane label="可视化地图" name="nine">可视化地图</el-tab-pane>
        <el-tab-pane label="会务管理" name="nine">会务管理</el-tab-pane>
      </el-tabs>
    </vab-card>
  </div>
</template>

<script lang="ts" setup>
const activeName = ref<any>('first')
const tableData = ref<any>([
  {
    date: '2016-05-03',
    name: '王小虎',
    province: 'IT部门',
    city: '视频会议',
    address: 'xxx会议',
  },
  {
    date: '2016-05-03',
    name: '王小虎',
    province: 'IT部门',
    city: '视频会议',
    address: 'xxx会议',
  },
  {
    date: '2016-05-03',
    name: '王小虎',
    province: 'IT部门',
    city: '视频会议',
    address: 'xxx会议',
  },
  {
    date: '2016-05-03',
    name: '王小虎',
    province: 'IT部门',
    city: '视频会议',
    address: 'xxx会议',
  },
  {
    date: '2016-05-03',
    name: '王小虎',
    province: 'IT部门',
    city: '视频会议',
    address: 'xxx会议',
  },
  {
    date: '2016-05-03',
    name: '王小虎',
    province: 'IT部门',
    city: '视频会议',
    address: 'xxx会议',
  },
  {
    date: '2016-05-03',
    name: '王小虎',
    province: 'IT部门',
    city: '视频会议',
    address: 'xxx会议',
  },
  {
    date: '2016-05-03',
    name: '王小虎',
    province: 'IT部门',
    city: '视频会议',
    address: 'xxx会议',
  },
])
</script>
<template>
  <vab-card :body-style="{ height: '210px' }" skeleton>
    <template #header>
      <vab-icon icon="donut-chart-fill" />
      会议类型
    </template>
    <vab-chart :option="option" />
  </vab-card>
</template>

<script lang="ts" setup>
import { useSettingsStore } from '/@/store/modules/settings'

const settingsStore = useSettingsStore()
const { color } = storeToRefs(settingsStore)
const option = reactive<any>({
  tooltip: {
    trigger: 'item',
  },
  series: [
    {
      name: '会议类型',
      type: 'pie',
      radius: ['40%', '80%'],
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2,
      },
      data: [
        { value: 1048, name: '本地会议1048次' },
        { value: 735, name: '视频会议735次' },
      ],
    },
  ],
})

watch(
  color,
  () => {
    option.color = [color.value]
  },
  { immediate: true }
)
</script>
<template>
  <el-drawer v-model="dialogFormVisible" append-to-body :before-close="close" direction="rtl" size="80%" :title="title">
    <el-row :gutter="20">
      <el-col :lg="6" :md="12" :sm="24" :xl="6" :xs="24">
        <meeting-type />
      </el-col>
      <el-col :lg="10" :md="12" :sm="24" :xl="10" :xs="24">
        <meeting-report />
      </el-col>
      <el-col :lg="8" :md="12" :sm="24" :xl="8" :xs="24">
        <meeting-rank />
      </el-col>
      <el-col :lg="24" :md="24" :sm="24" :xl="24" :xs="24">
        <meeting-tab />
      </el-col>
    </el-row>
  </el-drawer>
</template>

<script lang="ts" setup>
import MeetingType from '/@/views/sence/meetingroom/vabAutoComponents/MeetingType.vue'
defineOptions({
  name: 'RoomDetailPanel',
})
const emit = defineEmits(['fetch-data'])
const title = ref<string>('')
const dialogFormVisible = ref<boolean>(false)
const showEdit = (row: any) => {
  if (!row) {
    title.value = '大会议室-32F'
  } else {
    title.value = '编辑'
  }
  dialogFormVisible.value = true
}
defineExpose({
  showEdit,
})
const close = () => {
  emit('fetch-data')
  dialogFormVisible.value = false
}
</script>
<template>
  <div class="meeting-calendar-container auto-height-container">
    <meeting-calendar />
  </div>
</template>
<script lang="ts" setup>
import MeetingCalendar from '/@/views/sence/meetingroom/vabAutoComponents/MeetingCalendar.vue'
defineOptions({
  name: 'MeetingRoom',
})
</script>
<template>
  <div class="booklist-container no-background-container auto-height-container">
    <el-row :gutter="20">
      <el-col :lg="5" :md="24" :sm="24" :xl="4" :xs="24">
        <vab-card class="auto-height-card1">
          <el-tree
            ref="treeRef"
            v-loading="treeLoading"
            :data="spacedata"
            default-expand-all
            :highlight-current="true"
            node-key="id"
            :props="defaultProps"
            @node-click="handleNodeClick"
          />
        </vab-card>
      </el-col>
      <el-col :lg="19" :md="24" :sm="24" :xl="20" :xs="24">
        <vab-card class="auto-height-card">
          <vab-query-form>
            <vab-query-form-top-panel>
              <!-- <el-form inline label-width="49px" :model="queryForm" @submit.prevent>
                <el-form-item label="名称">
                  <el-input v-model="queryForm.title" clearable placeholder="请输入会议室名称" />
                </el-form-item>
                <el-form-item>
                  <el-button :icon="Search" :loading="listLoading" native-type="submit" type="primary" @click="queryData">查询</el-button>
                </el-form-item>
              </el-form> -->
            </vab-query-form-top-panel>
            <vab-query-form-left-panel>
              <el-breadcrumb :separator-icon="ArrowRight">
                <el-breadcrumb-item v-for="(item, index) in crumblist" :key="index">
                  {{ item }}
                </el-breadcrumb-item>
              </el-breadcrumb>
            </vab-query-form-left-panel>

          </vab-query-form>
          <el-table
            ref="tableRef"
            v-loading="listLoading"
            :border="border"
            :data="list"
            :size="lineHeight"
            :stripe="stripe"
            @selection-change="setSelectRows"
          >
            <el-table-column type="selection" width="38" />
            <el-table-column align="center" label="ID" :min-width="20" prop="id" show-overflow-tooltip :sortable="true" />
            <el-table-column align="center" label="会议室"  prop="meetingRoomName" show-overflow-tooltip :sortable="true" />
            <el-table-column align="center" label="会议主题" :min-width="80" prop="meetingSubject" show-overflow-tooltip :sortable="true" />
            <el-table-column align="center" label="会议日期"  prop="startTime" show-overflow-tooltip :sortable="true" >
              <template #default="{ row }">
                {{ moment.unix(row.startTime).format('MM-DD') }}
              </template>
            </el-table-column>
            <el-table-column align="center" label="会议时间"  prop="endTime" show-overflow-tooltip :sortable="true" >
              <template #default="{ row }">
                {{ moment.unix(row.startTime).format('HH:mm') }}-{{ moment.unix(row.endTime).format('HH:mm') }}
              </template>
            </el-table-column>
            <el-table-column align="center" label="会议状态"  prop="statusName" show-overflow-tooltip :sortable="true" >
              <template #default="{ row }">
                <el-tag :type="statusFilter(row.status)">
                  {{ row.statusName }}
                </el-tag>
              </template>
            </el-table-column>

            <!--            <el-table-column align="center" label="状态" :min-width="80" prop="deleteFlag" show-overflow-tooltip :sortable="true">-->
            <!--              <template #default="{ row }">-->
            <!--                <span>-->
            <!--                  <el-switch v-model="row.deleteFlag" active-text="启用" disabled inactive-text="未启用" inline-prompt />-->
            <!--                </span>-->
            <!--              </template>-->
            <!--            </el-table-column>-->
            <!-- <el-table-column align="center" :fixed="fixed" label="操作" width="170">
              <template #header>
                <el-checkbox v-model="fixed" label="操作" true-value="right" />
              </template>
              <template #default="{ row }">
                <el-button link type="primary" @click="handleDelete(row)">结束</el-button>
              </template>
            </el-table-column> -->
            <template #empty>
              <el-empty class="vab-data-empty" description="暂无数据" />
            </template>
          </el-table>
          <vab-pagination
            :current-page="queryForm.pageNo"
            :page-size="queryForm.pageSize"
            :total="total"
            @current-change="handleCurrentChange"
            @size-change="handleSizeChange"
          />
        </vab-card>
      </el-col>
    </el-row>
    <mroom-edit ref="editRef" :data="queryForm" @fetch-data="fetchData" />
    <el-dialog v-model="mapDialogVisible" append-to-body draggable :title="currentItem.name" width="80%" @close="closeMap">
      <div v-loading="mapLoading" class="map-panel-container">
        <div id="map" class="mapcontainer"></div>
      </div>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { Plus, Search } from '@element-plus/icons-vue'
import { ArrowRight } from '@element-plus/icons-vue'
import { getTreeByFloor } from '/@/api/spaceManagement'
import { ElMessage, ElMessageBox, ElTree } from 'element-plus'
import icon from '/@/assets/marker.png'
import { getServiceUrl } from '~/src/utils'
import { getOrder } from '~/src/api/sence'
import moment from 'moment-timezone'
const $baseConfirm = inject<any>('$baseConfirm')
const $baseMessage = inject<any>('$baseMessage')
defineOptions({
  name: 'MroomTable',
})
const currentMarker = ref<any>()
const currentNode = ref<any>()
const crumblist = ref<any>([])
const tableRef = ref<any>(null)
const editRef = ref<any>(null)
const map = ref<any>(null)
const border = ref<boolean>(true)
const stripe = ref<boolean>(false)
const mapDialogVisible = ref<boolean>(false)
const lineHeight = ref<any>('default')
const list = ref<any>([])
const listLoading = ref<boolean>(true)
const treeLoading = ref<boolean>(true)
const mapLoading = ref<boolean>(false)
const total = ref<any>(0)
const selectRows = ref<any>([])
const currentItem = ref<any>({})
const queryForm = reactive<any>({
  spaceCode: '',
  floorAreaCode: '',
  floorCode: '',
  areaCode: '',
  areaType: '',
  pageNo: 1,
  pageSize: 50,
  title: '',
  type: 'all',
})
//tree node start
const treeRef = ref<InstanceType<typeof ElTree>>()
const spacedata = ref<any>([])
const handleNodeClick = (treenode: any) => {
  currentNode.value = treenode
  queryForm.spaceCode = ''
  queryForm.floorAreaCode = ''
  queryForm.floorCode = ''
  queryForm.areaCode = ''
  queryForm.areaType = ''
  if (treenode.spaceCode) {
    queryForm.spaceCode = treenode.spaceCode
  }
  if (treenode.floorAreaCode) {
    queryForm.floorAreaCode = treenode.floorAreaCode
  }
  if (treenode.floorCode) {
    queryForm.floorCode = treenode.floorCode
  }
  if (treenode.areaCode) {
    queryForm.areaCode = treenode.areaCode
  }
  if (treenode.areaType) {
    queryForm.areaType = treenode.areaType
  }

  if (treenode.floorCode) {
    //只有选择到了区域才进行查询
    queryForm.floorCode = treenode.floorCode
    crumblist.value = treenode.crumblist
    fetchData()
  }
}
const statusFilter = (status: string | number) => {
  const statusMap: any = {//0未开始 1进行中 2已结束 3已取消
    0: 'info',
    1: 'primary',
    2: 'success',
    3: 'danger',
  }
  return statusMap[status]
}
const defaultProps = {
  children: 'children',
  label: 'label',
}
//tree node end
const fixed = ref<string>('right')
const fetchData = async () => {
  listLoading.value = true
  const { data } = await getOrder(queryForm)
  console.info(data)
  list.value = data
  total.value = data.total
  listLoading.value = false
}

const fetchSpaceData = async () => {
  treeLoading.value = true
  const { data } = await getTreeByFloor()
  spacedata.value = data.floorTree
  treeLoading.value = false
  return spacedata.value
}

const handleSizeChange = (value: number) => {
  queryForm.pageNo = 1
  queryForm.pageSize = value
  fetchData()
}

const handleCurrentChange = (value: number) => {
  queryForm.pageNo = value
  fetchData()
}

const queryData = () => {
  queryForm.pageNo = 1
  fetchData()
}
const closeMap = () => {
  currentItem.value = {}
  mapDialogVisible.value = false
  if(map.value!=null){map.value.dispose()}
  map.value = null
}
function handleDefaultClick(e) {
  console.log(e)
  if (e.target.isMesh) {
    e.target.active()
  }
  ElMessageBox.confirm('是否确认为当前区域添加坐标?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
      // new AirocovMap.covers.ImageMarker({
      //   name: 'device',
      //   imgSrc: icon,
      //   size: 14,
      //   position: {
      //     x: Number(e.target.info.center[0]),
      //     y: 1,
      //     z: Number(e.target.info.center[1]),
      //   },
      //   canvasHeight: map.value.dom.offsetHeight,
      //   fontSize: 70,
      //   info: e.target.info.name,
      //   callback: function (marker) {
      //     marker.material.depthTest = false
      //     map.value.addToMap({
      //       object: marker,
      //       floorName: queryForm.floorCode,
      //       layerName: 'device',
      //       isClick: true, // 标记为可点击
      //     })
      //   },
      // })
      if(currentMarker.value){
        currentMarker.value.remove()
      }
      addMark(e.position.x,e.position.z)
      const res = await setMapPosition({
        id: currentItem.value.id,
        type: "meetingroom",
        posX: e.position.x,
        posY: 1,
        posZ: e.position.z,
      })
      if (res.code === '200') {
        ElMessage.success('添加成功')
        closeMap()
        handleNodeClick(currentNode.value)
      } else {
        ElMessage.error(res.msg)
      }
    })
    .catch(() => {})
}
const handleSelect = (selection: any) => {
  currentItem.value = selection
  mapDialogVisible.value = true
  mapLoading.value = true
  setTimeout(() => {
    map.value = new AirocovMap.Map({
      container: document.getElementById('map'),
      mapUrl: `${getServiceUrl()}/${selection.floorCode}.acmap`,
      themeUrl: '/os/static/theme/theme.json',
      floorSwitch: { show: false },
      opacity: 0.6,
      mergeModels: ['wall', 'plane', 'door'],
      clickModels: ['floor', 'plane', 'room', 'area', 'wall', 'logo'],
      key: 'KMED1W0N50YIWIYJCUNLYPMJ49JDLASE',
      defaultFloorIndex: 0,
      showAllFloor: false,
      maxPolarAngle: 90,
      pointScale: 1.4,
      zoom: 0.8,
      bgColor: 'transparent',
      showViewMode: '2D',
      clickIntoBuilding: false,
      font: {
        fontscale: 200,
        iconScale: 5,
        indent: 100,
      },
      pointscale: 5,
      onReady: function () {
        // map.render.camera.control.autoRotate = true;
        if(selection.posX!=null){
          addMark(selection.posX,selection.posZ)
            //  new AirocovMap.covers.ImageMarker({
            //     name: 'device',
            //     imgSrc: icon,
            //     size: 32,
            //     position: {
            //       x: Number(selection.posX),
            //       y: 1,
            //       z: Number(selection.posZ),
            //     },
            //     canvasHeight: map.value.dom.offsetHeight,
            //     fontSize: 70,
            //     floorName:selection.floorCode,
            //     // info: selection.floorCode+"_"+selection.name,
            //     callback: function (imgMark:any) {
            //       //将图片标注添加到地图指定楼层的指定图层
            //       currentMarker.value = imgMark
            //       map.value.addToMap({
            //         object: imgMark,
            //         floorName:selection.floorCode,
            //         layerName: 'device',
            //       });
            //     },
            //   });
          }
      },
    })
    new AirocovMap.controls.ModeSwitch(map.value, {
      left: '10px', //控件与容器左侧距离，或添加right属性，设置与容器右侧距离
      bottom: '40px', //控件与容器底部距离，或添加top属性，设置与容器顶部距离
      //点击按钮的回调方法,返回type表示按钮类型,value表示对应的功能值
      clickCallBack: function (type) {
        //console.log(type);
        //console.log(map.render.camera.object)
      },
    })
    new AirocovMap.controls.Compass(map.value, {
      width: '48px', //指北针大小
      left: '10px', //控件与容器左侧距离，或添加right属性，设置与容器右侧距离
      bottom: '130px', //控件与容器顶部距离，或添加bottom属性，设置与容器底部距离
    })
    map.value.event.on('click', handleDefaultClick)
    mapLoading.value = false
  }, 1000)
}
const setSelectRows = (value: any) => {
  selectRows.value = value
}
const handleEdit = (row: any) => {
  editRef.value.showEdit(row)
}
function addMark(x,z){
  new AirocovMap.covers.ImageMarker({
        name: 'device',
        imgSrc: icon,
        size: 32,
        position: {
          x: Number(x),
          y: 1,
          z: Number(z),
        },
        canvasHeight: map.value.dom.offsetHeight,
        fontSize: 70,
        // info: currentItem.value.floorCode+"_"+currentItem.value.name,
        callback: function (marker:any) {
          currentMarker.value = marker
          marker.material.depthTest = false
          map.value.addToMap({
            object: marker,
            floorName:currentItem.value.floorCode,
            layerName: 'device',
            isClick: true, // 标记为可点击
          })
        },
      })
}
onActivated(() => {
  tableRef.value.doLayout()
})
const getFirstArea = (arr: any) => {
  for (let i = 0; i < arr.length; i++) {
    if (arr[i].type == 'floor') {
      return arr[i].id
    }
    if (arr[i].children) {
      return getFirstArea(arr[i].children)
    }
  }
  return ''
}
const handleAdd = () => {
  editRef.value.showEdit()
}
const handleDelete = (row: any) => {
  if (row.id) {
    $baseConfirm('您确定要删除当前项吗', null, async () => {
      const { msg }: any = await doMroomDelete({ ids: row.id })
      $baseMessage(msg, 'success', 'hey')
      await fetchData()
    })
  }
}
onBeforeMount(() => {
  const returnTreeData = fetchSpaceData()
  returnTreeData.then(() => {
    const firstAreaId = getFirstArea(spacedata.value)
    treeRef.value.setCurrentKey(firstAreaId)
    // console.info(treeRef.value.getNode('33333').data)
    handleNodeClick(treeRef.value.getNode(firstAreaId).data)
  })
})
onUnmounted(() => {
  if(map.value!=null)map.value.dispose()
  map.value = null
})
</script>

<style lang="scss" scoped>
.booklist-container {
  width: 100%;
  :deep() {
    .el-card {
      margin-bottom: 0;
    }
  }
}
.map-panel-container {
  :deep() {
    .mapcontainer {
      padding-top: 20px;
      height: calc(var(--el-container-height) - var(--el-padding) - 52px) !important;
    }
    .airocovFloorSwitch {
      top: 80px !important;
      left: 20px !important;
    }
  }
}
</style>
<template>
  <div>
    <el-button :icon="Refresh" type="info">同步会议室</el-button>
    <el-button-group style="padding-left: 10px">
      <el-button type="info">三区</el-button>
      <el-button type="info">四区</el-button>
      <el-button type="info">五区</el-button>
    </el-button-group>
    <el-button-group style="padding-left: 10px">
      <el-button :icon="Menu" type="default" @click="viewtype = 'sand'">沙盘</el-button>
      <el-button :icon="Reading" type="default" @click="viewtype = 'map'">地图</el-button>
    </el-button-group>
    <space-panel v-if="viewtype == 'sand'" :spaces-data="spacedata" spaces-type="meeting" @open-dialog="hideAddPanel" />
    <map-panel v-if="viewtype == 'map'" map-id="meetingroom" />
    <room-detail-panel ref="editRef" @fetch-data="fetchData" />
  </div>
</template>
<script lang="ts" setup>
import { onMounted, ref, reactive } from 'vue'
import SpacePanel from '/@vab/components/SpacePanel/index.vue'
import RoomDetailPanel from '/@/views/sence/meetingroom/vabAutoComponents/RoomDetailPanel.vue'
import { Refresh, Reading, Menu } from '@element-plus/icons-vue'
import { useUserStore } from '/@/store/modules/user.ts'
import { getMRoomList } from '/@/api/space.ts'
import { getSpaceFloorList } from '/@/api/space'
const userStore = useUserStore()
const { spaceCode } = storeToRefs(userStore)
const viewtype = ref<string>('sand')
const editRef = ref<any>(null)
defineOptions({
  name: 'MeetingRoom',
})

onMounted(() => {
  fetchMeetingRoomData()
  fetchSpaceData()
  updateSpaceData()
})
const spacedata = ref<any>([])
const spacedata1 = [
  {
    floor: '21F',
    desc: '1321m²',
    rooms: [],
  },
  {
    floor: '23F',
    desc: '2321m²',
    rooms: [
      {
        name: '会议室1',
        hasperson: true,
        sensor: [
          { title: '', status: 'online' },
          { title: '', status: 'online' },
          { title: '', status: 'offline' },
          { title: '', status: 'online' },
          { title: '', status: 'online' },
        ],
      },
      {
        name: '会议室2',
        hasperson: false,
        sensor: [
          { title: '', status: 'offline' },
          { title: '', status: 'offline' },
          { title: '', status: 'offline' },
        ],
      },
    ],
  },
  {
    floor: '24F',
    desc: '1321m²',
    rooms: [
      {
        name: '大会议室',
        hasperson: false,
        sensor: [
          { title: '', status: 'online' },
          { title: '', status: 'online' },
          { title: '', status: 'offline' },
          { title: '', status: 'online' },
          { title: '', status: 'online' },
        ],
      },
      {
        name: '会议室2',
        hasperson: false,
        sensor: [
          { title: '', status: 'offline' },
          { title: '', status: 'offline' },
          { title: '', status: 'offline' },
        ],
      },
      {
        name: '会议室3',
        hasperson: false,
        sensor: [
          { title: '', status: 'offline' },
          { title: '', status: 'offline' },
          { title: '', status: 'offline' },
        ],
      },
      {
        name: '会议室4',
        hasperson: true,
        sensor: [
          { title: '', status: 'offline' },
          { title: '', status: 'offline' },
          { title: '', status: 'offline' },
        ],
      },
      {
        name: '会议室5',
        hasperson: false,
        sensor: [
          { title: '', status: 'offline' },
          { title: '', status: 'offline' },
          { title: '', status: 'offline' },
        ],
      },
      {
        name: '会议室6',
        hasperson: false,
        sensor: [
          { title: '', status: 'offline' },
          { title: '', status: 'offline' },
          { title: '', status: 'offline' },
        ],
      },
      {
        name: '会议室7',
        hasperson: false,
        sensor: [
          { title: '', status: 'offline' },
          { title: '', status: 'offline' },
          { title: '', status: 'offline' },
        ],
      },
      {
        name: '会议室8',
        hasperson: false,
        sensor: [
          { title: '', status: 'offline' },
          { title: '', status: 'offline' },
          { title: '', status: 'offline' },
        ],
      },
    ],
  },
  {
    floor: '25F',
    desc: '1321m²',
    rooms: [],
  },
  {
    floor: '26F',
    desc: '1321m²',
    rooms: [],
  },
  {
    floor: '27F',
    desc: '1321m²',
    rooms: [],
  },
  {
    floor: '28F',
    desc: '1321m²',
    rooms: [],
  },
  {
    floor: '29F',
    desc: '1321m²',
    rooms: [],
  },
  {
    floor: '30F',
    desc: '1321m²',
    rooms: [],
  },
  {
    floor: '31F',
    desc: '1321m²',
    rooms: [],
  },
  {
    floor: '32F',
    desc: '2321m²',
    rooms: [
      {
        name: '会议室1',
        hasperson: true,
        sensor: [
          { title: '', status: 'online' },
          { title: '', status: 'online' },
          { title: '', status: 'offline' },
          { title: '', status: 'online' },
          { title: '', status: 'online' },
        ],
      },
      {
        name: '会议室2',
        hasperson: false,
        sensor: [
          { title: '', status: 'offline' },
          { title: '', status: 'offline' },
          { title: '', status: 'offline' },
        ],
      },
    ],
  },
]



const roomlist = ref<any>([])
const queryForm = reactive<any>( {
    spaceCode: spaceCode.value,
    floorAreaCode: '',
    floorCode: '',
    areaCode: '',
    areaType: '',
    pageNo: 1,
    pageSize: 500,
    title: '',
})
const fetchMeetingRoomData = async() => {
  const { data } = await getMRoomList(queryForm)
  roomlist.value = data.list
  console.log('获取到的会议室列表:', roomlist.value)
  fetchSpaceData()
}
const areas = ref([])
const floors = ref<any>([])
const fetchSpaceData = async () => {
  const { data } = await getSpaceFloorList({ spaceCode: spaceCode.value })
  floors.value = data.SpaceFloorList
  areas.value = data.SpaceFloorAreaList
  console.log('获取到的楼层列表:', floors.value)
  console.log('获取到的区域列表:', areas.value)
  updateSpaceData()
}

const hideAddPanel = (item: any) => {
  console.info(item)
  console.info('+++++++++++++++++++++++++++')
  // this.fetchData();
  editRef.value.showEdit()
  // editRef.value.showEdit()
}

const combineFloorAndRooms = () => {
  if (!floors.value || !roomlist.value) return []
  
  // 按楼层分组会议室
  const roomsByFloor = roomlist.value.reduce((acc, room) => {
    const floorCode = room.floorCode
    if (!acc[floorCode]) {
      acc[floorCode] = []
    }
    acc[floorCode].push(room)
    return acc
  }, {})
  
  // 创建最终数据结构
  return floors.value.map(floor => {
    // 获取当前楼层的会议室
    const floorRooms = roomsByFloor[floor.floorCode] || []
    
    // 转换会议室格式
    const formattedRooms = floorRooms.map(room => {
      return {
        name: room.name,
        hasperson: true,
        sensor: [
          { title: '1', status: 'online' },
          { title: '1', status: 'offline' },
          { title: '1', status: 'offline' }
        ]
      }
    })
    
    return {
      floor: floor.floorName,
      desc: floor.floorSquare ? `${floor.floorSquare}m²` : '0m²',
      rooms: formattedRooms
    }
  }).sort((a, b) => {
    // 提取数字部分进行排序
    const numA = parseInt(a.floor.replace(/\D/g, '')) || 0
    const numB = parseInt(b.floor.replace(/\D/g, '')) || 0
    return numA - numB
  })
}

// 更新 spacedata
const updateSpaceData = () => {
  if (floors.value?.length && roomlist.value?.length) {
    const combinedData = combineFloorAndRooms()
    // 使用 Vue 的响应式更新方法
    // spacedata.splice(0, spacedata.length, ...combinedData)
    spacedata.value = combinedData
    console.log('更新后的 spacedata:', spacedata)
  }
}

// 确保在组件挂载时获取数据
onMounted(() => {
  fetchMeetingRoomData()

})

</script>

<template>
  <div class="timestatics-container no-background-container">
    <vab-query-form>
      <vab-query-form-top-panel>
        <el-form inline label-width="60px" :model="queryForm" @submit.prevent>
          <el-form-item label="日期">
            <el-date-picker 
              v-model="queryForm.dateRange" 
              type="daterange" 
              value-format="YYYY-MM-DD" 
              range-separator="至" 
              start-placeholder="开始日期" 
              end-placeholder="结束日期"
              :default-time="[
                new Date(2000, 1, 1, 0, 0, 0),
                new Date(2000, 1, 1, 23, 59, 59)
              ]"
            />
          </el-form-item>
          <el-form-item>
            <el-button :icon="Search" :loading="loading" type="primary" @click="fetchStatData">查询</el-button>
          </el-form-item>
        </el-form>
      </vab-query-form-top-panel>
    </vab-query-form>
    
    <el-row :gutter="20">
      <el-col :span="12">
        <car-num background="white" percentage="30%" :countConfig="{endValue: totalBookings}" icon="account-circle-fill" title="总会议次数">
          <template #tag>
            <el-tag type="danger">{{ queryDate }}</el-tag>
          </template>
        </car-num>
      </el-col>
      <el-col :span="12">
        <car-num background="white" percentage="30%" :countConfig="{endValue: totalMeetingTime}" icon="time-line" title="总会议时长(分钟)">
          <template #tag>
            <el-tag type="danger">{{ queryDate }}</el-tag>
          </template>
        </car-num>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <vab-card :body-style="{ height: '300px' }" skeleton>
          <template #header>
            <vab-icon icon="bar-chart-2-line" />
            各企业会议次数对比
          </template>
          <vab-chart :option="bookingChartOption" />
        </vab-card>
      </el-col>
      <el-col :span="12">
        <vab-card :body-style="{ height: '300px' }" skeleton>
          <template #header>
            <vab-icon icon="bar-chart-2-line" />
            各企业会议时长对比(分钟)
          </template>
          <vab-chart :option="timeChartOption" />
        </vab-card>
      </el-col>
    </el-row>
  </div>
</template>
<script lang="ts" setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { timestatics } from '/@/api/sence.ts'
import { Search } from '@element-plus/icons-vue'
import moment from "moment";

defineOptions({
  name: 'meetingTimeStatics',
})

const loading = ref<boolean>(false)
const queryForm = reactive<any>({
  dateRange: [
    moment().startOf('month').format('YYYY-MM-DD'),
    moment().endOf('month').format('YYYY-MM-DD')
  ]
})
const queryDate = ref(`${moment().startOf('month').format('YYYY-MM-DD')} 至 ${moment().endOf('month').format('YYYY-MM-DD')}`);
const meetingData = ref<any>([])

// 计算总会议次数和总会议时长
const totalBookings = computed(() => {
  const allOrg = meetingData.value.find(item => item.orgId === 0)
  return allOrg ? allOrg.bookingNum : 0
})

const totalMeetingTime = computed(() => {
  const allOrg = meetingData.value.find(item => item.orgId === 0)
  return allOrg ? allOrg.meetingTime : 0
})

// 准备图表数据
const orgNames = computed(() => {
  return meetingData.value
    .filter(item => item.orgId !== 0) // 排除"全部企业"
    .map(item => item.orgName)
})

const bookingNums = computed(() => {
  return meetingData.value
    .filter(item => item.orgId !== 0) // 排除"全部企业"
    .map(item => item.bookingNum)
})

const meetingTimes = computed(() => {
  return meetingData.value
    .filter(item => item.orgId !== 0) // 排除"全部企业"
    .map(item => item.meetingTime)
})

// 会议次数图表配置
const bookingChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: [
    {
      type: 'category',
      data: orgNames.value,
      axisTick: {
        alignWithLabel: true
      },
      axisLabel: {
        interval: 0,
        rotate: 30,
        textStyle: {
          fontSize: 12
        }
      }
    }
  ],
  yAxis: [
    {
      type: 'value'
    }
  ],
  series: [
    {
      name: '会议次数',
      type: 'bar',
      barWidth: '60%',
      data: bookingNums.value,
      label: {
        show: true,
        position: 'inside',
        formatter: '{c}',
        fontSize: 14,
        color: '#fff'
      }
    }
  ]
}))

// 会议时长图表配置
const timeChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: [
    {
      type: 'category',
      data: orgNames.value,
      axisTick: {
        alignWithLabel: true
      },
      axisLabel: {
        interval: 0,
        rotate: 30,
        textStyle: {
          fontSize: 12
        }
      }
    }
  ],
  yAxis: [
    {
      type: 'value'
    }
  ],
  series: [
    {
      name: '会议时长(分钟)',
      type: 'bar',
      barWidth: '60%',
      data: meetingTimes.value,
      label: {
        show: true,
        position: 'inside',
        formatter: '{c}',
        fontSize: 14,
        color: '#fff'
      }
    }
  ]
}))

const fetchStatData = async () => {
  loading.value = true
  
  // 更新显示的日期范围
  if (queryForm.dateRange && queryForm.dateRange.length === 2) {
    queryDate.value = `${queryForm.dateRange[0]} 至 ${queryForm.dateRange[1]}`;
  } else {
    // 如果没有选择日期范围，默认使用当月
    const startOfMonth = moment().startOf('month').format('YYYY-MM-DD');
    const endOfMonth = moment().endOf('month').format('YYYY-MM-DD');
    queryDate.value = `${startOfMonth} 至 ${endOfMonth}`;
    queryForm.dateRange = [startOfMonth, endOfMonth];
  }
  
  try {
    const { data } = await timestatics({
      startDay: queryForm.dateRange[0],
      endDay: queryForm.dateRange[1],
      spaceCode: 'KJY-CD'
    })
    
    meetingData.value = data
    console.log("会议数据", data)
  } catch (error) {
    console.error("获取数据失败", error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStatData()
})
</script>

<style lang="scss" scoped>
.timestatics-container {
  width: 100%;
}
</style>

```

## 后30页
```
import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';
import { ApiProperty } from '@nestjs/swagger';

/**
 * Meeting Schedule entity
 */
@Entity('meeting')
export class Meeting {
  @ApiProperty({ description: 'ID' })
  @PrimaryGeneratedColumn()
  id: number;

  @ApiProperty({ description: '会议室ID' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '会议室ID',
    nullable: false,
  })
  meetingRoomId: string;

  @ApiProperty({ description: '会议室名称' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '会议室名称',
    nullable: false,
  })
  meetingRoomName: string;

  @ApiProperty({ description: '会议室容量' })
  @Column({
    type: 'int',
    comment: '会议室容量',
    nullable: true,
  })
  capacity: number;

  @ApiProperty({ description: '开始时间' })
  @Column({
    type: 'bigint',
    comment: '开始时间',
    nullable: false,
  })
  startTime: number;

  @ApiProperty({ description: '结束时间' })
  @Column({
    type: 'bigint',
    comment: '结束时间',
    nullable: false,
  })
  endTime: number;

  @ApiProperty({ description: '状态', enum: ['0', '1', '2'] })
  @Column({
    type: 'int',
    comment: '状态',
    nullable: true,
    default: 0,
  })
  status: number;

  @ApiProperty({ description: '预订人ID' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '预订人ID',
    nullable: true,
  })
  booker: string;

  @ApiProperty({ description: '预订ID' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '预订ID',
    nullable: true,
  })
  bookingId: string;

  @ApiProperty({ description: '日程ID' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '日程ID',
    nullable: true,
  })
  scheduleId: string;

  @ApiProperty({ description: '会议主题' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '会议主题',
    nullable: true,
  })
  meetingSubject: string;

  @ApiProperty({ description: '预订人部门' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '预订人部门',
    nullable: true,
  })
  bookerDept: string;

  @ApiProperty({ description: '预订人姓名' })
  @Column({
    type: 'varchar',
    length: 255,
    comment: '预订人姓名',
    nullable: true,
  })
  bookerName: string;

  @ApiProperty({ description: '创建时间' })
  @Column({
    type: 'varchar',
    length: 20,
    comment: '创建时间',
    nullable: true,
    default: '',
  })
  createTime: string;
}
import { Controller, Get, Post, Body, Query, UseGuards, BadRequestException, Request } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBody, ApiBearerAuth } from '@nestjs/swagger';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

import { MeetingService, GetMeetingScheduleParams, MeetingRoomWithSchedule, SpaceFloorListDto, SpaceFloorResponseDto } from './meeting.service';
import { SceneJsonResponseDto } from './dto/scene-json.dto';
interface RequestWithUser extends Request {
  user: {
    userId: number;
    realName: string;
    spaceCode?: string;
  };
}
@ApiTags('会议管理')
@Controller('meeting')
export class MeetingController {
  constructor(private readonly meetingService: MeetingService) {}

  @Get('getMeetingRoomAndOrder')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: '获取会议室楼层和区域', description: '获取指定空间的会议室楼层和区域信息' })
  @ApiResponse({
    status: 200,
    description: '获取成功',
    schema: {
      properties: {
        code: { type: 'string', example: '200' },
        msg: { type: 'string', example: 'success' },
        data: {
          type: 'object',
          properties: {
            SpaceFloorList: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  id: { type: 'number' },
                  floorNum: { type: 'string' },
                  floorCode: { type: 'string' },
                  floorName: { type: 'string' },
                  areaCode: { type: 'string' },
                  floorSquare: { type: 'number' },
                  areaId: { type: 'string' },
                  officeArea: { type: 'number' },
                  floorArea: { type: 'number' }
                }
              }
            },
            SpaceFloorAreaList: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  areaId: { type: 'number' },
                  areaCode: { type: 'string' },
                  areaName: { type: 'string' }
                }
              }
            }
          }
        }
      }
    }
  })
  async getMeetingRoomAndOrder(@Query() params: SpaceFloorListDto): Promise<{ code: string; msg: string; data: any }> {
    try {
      const result = await this.meetingService.getMeetingRoomAndOrder(params);
      return {
        code: '200',
        msg: 'success',
        data: result.data
      };
    } catch (error) {
      throw new BadRequestException({
        code: '400',
        msg: `获取失败: ${error.message}`
      });
    }
  }

  @Get('getSchedule')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: '获取会议室日程', description: '获取指定会议室或时间范围内的会议日程' })
  @ApiResponse({
    status: 200,
    description: '获取成功',
    schema: {
      properties: {
        code: { type: 'string', example: '200' },
        msg: { type: 'string', example: 'success' },
        data: {
          type: 'object',
          properties: {
            list: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  meetingRoomId: { type: 'string', example: '700' },
                  meetingRoomName: { type: 'string', example: '23F-2301' },
                  capacity: { type: 'number', example: 12 },
                  schedule: {
                    type: 'array',
                    items: {
                      type: 'object',
                      properties: {
                        startTime: { type: 'number', example: 1747099800 },
                        endTime: { type: 'number', example: 1747108800 },
                        status: { type: 'string', example: '0' },
                        booker: { type: 'string', example: '0425855' },
                        bookingId: { type: 'string' },
                        scheduleId: { type: 'string' },
                        meetingSubject: { type: 'string', example: '新人训' },
                        bookerDept: { type: 'string', example: '服务体验' },
                        bookerName: { type: 'string', example: '徐佳' }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  })
  async getSchedule(@Query() params: GetMeetingScheduleParams) {
    return this.meetingService.getMeetingSchedule(params);
  }

  @Post('saveSchedule')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: '保存会议室日程', description: '保存会议室日程信息' })
  @ApiBody({
    schema: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          meetingRoomId: { type: 'string', example: '700' },
          meetingRoomName: { type: 'string', example: '23F-2301' },
          capacity: { type: 'number', example: 12 },
          schedule: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                startTime: { type: 'number', example: 1747099800 },
                endTime: { type: 'number', example: 1747108800 },
                status: { type: 'string', example: '0' },
                booker: { type: 'string', example: '0425855' },
                bookingId: { type: 'string' },
                scheduleId: { type: 'string' },
                meetingSubject: { type: 'string', example: '新人训' },
                bookerDept: { type: 'string', example: '服务体验' },
                bookerName: { type: 'string', example: '徐佳' }
              }
            }
          }
        }
      }
    }
  })
  @ApiResponse({
    status: 200,
    description: '保存成功',
    schema: {
      properties: {
        code: { type: 'string', example: '200' },
        msg: { type: 'string', example: 'success' }
      }
    }
  })
  async saveSchedule(@Body() data: MeetingRoomWithSchedule[]) {
    return this.meetingService.saveMeetingSchedule(data);
  }

  @Post('deleteSchedule')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: '删除会议室日程', description: '根据bookingId删除会议室日程' })
  @ApiBody({
    schema: {
      type: 'object',
      properties: {
        bookingId: { type: 'string', example: 'AD2323-232DS2-232234' }
      },
      required: ['bookingId']
    }
  })
  @ApiResponse({
    status: 200,
    description: '删除成功',
    schema: {
      properties: {
        code: { type: 'string', example: '200' },
        msg: { type: 'string', example: 'success' }
      }
    }
  })
  async deleteSchedule(@Body() data: { bookingId: string }) {
    return this.meetingService.deleteMeetingSchedule(data.bookingId);
  }

  @Post('saveScheduleSimple')
  @ApiOperation({ summary: '简化的会议预定', description: '使用简化参数进行会议预定' })
  @ApiBody({
    schema: {
      type: 'object',
      properties: {
        meetingRoomCode: { type: 'string', example: 'M1001' },
        meetingTime: { type: 'string', example: '2025-6-5 22:30-23:00' },
        subject: { type: 'string', example: '何铮预定的会议' },
        unionid: { type: 'string', example: 'xxxxx' }
      },
      required: ['meetingRoomCode', 'meetingTime', 'subject', 'unionid']
    }
  })
  @ApiResponse({
    status: 200,
    description: '预定成功',
    schema: {
      properties: {
        code: { type: 'string', example: '200' },
        msg: { type: 'string', example: 'success' },
        data: {
          type: 'object',
          properties: {
            bookingId: { type: 'string', example: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx' }
          }
        }
      }
    }
  })
  async saveScheduleSimple(
    @Body() data: { meetingRoomCode: string; meetingTime: string; subject: string; unionid: string }
  ) {
    // 将整个data对象作为单个参数传递给服务方法
    return this.meetingService.saveMeetingScheduleSimple(data);
  }

  @Post('getMeetingList')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: '获取会议列表', description: '获取指定日期的所有会议预定' })
  @ApiBody({
    schema: {
      type: 'object',
      properties: {
        day: { type: 'string', example: '2025-06-06' }
      },
      required: ['day']
    }
  })
  @ApiResponse({
    status: 200,
    description: '获取成功',
    schema: {
      properties: {
        code: { type: 'string', example: '200' },
        msg: { type: 'string', example: 'success' },
        data: {
          type: 'object',
          properties: {
            list: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  roomId: { type: 'string', example: '163' },
                  roomCode: { type: 'string', example: 'M5103' },
                  roomName: { type: 'string', example: '5103会议室' },
                  meetingList: {
                    type: 'array',
                    items: {
                      type: 'object',
                      properties: {
                        name: { type: 'string', example: '曾慧' },
                        dept: { type: 'string', example: '财务会计' },
                        status: { type: 'number', example: 1 },
                        startTime: { type: 'string', example: '10:30' },
                        endTime: { type: 'string', example: '11:30' }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  })
  async getMeetingList(@Body() params: { day: string }) {
    try {
      const meetingList = await this.meetingService.getMeetingList(params.day);
      return {
        code: '200',
        msg: 'success',
        data: {
          list: meetingList
        }
      };
    } catch (error) {
      throw new BadRequestException({
        code: '400',
        msg: `获取会议列表失败: ${error.message}`
      });
    }
  }

  @Post('getOrder')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: '获取用户预定的会议', description: '获取当前登录用户在特定楼层或整个空间的会议预定' })
  @ApiBody({
    schema: {
      type: 'object',
      properties: {
        floorCode: { type: 'string', example: '2F' },
        spaceCode: { type: 'string', example: 'KJY-CD' }
      },
      required: ['floorCode', 'spaceCode']
    }
  })
  @ApiResponse({
    status: 200,
    description: '获取成功',
    schema: {
      properties: {
        code: { type: 'string', example: '200' },
        msg: { type: 'string', example: 'success' },
        data: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              id: { type: 'number' },
              meetingRoomId: { type: 'string' },
              meetingRoomName: { type: 'string' },
              startTime: { type: 'number' },
              endTime: { type: 'number' },
              meetingSubject: { type: 'string' },
              bookingId: { type: 'string' }
            }
          }
        }
      }
    }
  })
  async getOrder(
    @Body() params: { floorCode: string; spaceCode: string },
    @Request() req: RequestWithUser
  ) {
    try {
      // 从请求中获取用户ID
      const userId = req.user.userId;
      
      // 调用服务方法，传入用户ID和其他参数
      const result = await this.meetingService.getUserMeetingOrders({
        userId,
        floorCode: params.floorCode,
        spaceCode: params.spaceCode
      });
      
      return {
        code: '200',
        msg: 'success',
        data: result
      };
    } catch (error) {
      throw new BadRequestException({
        code: '400',
        msg: `获取用户会议预定失败: ${error.message}`
      });
    }
  }

  @Post('changeStatus')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: '修改会议状态', description: '取消或结束会议' })
  @ApiBody({
    schema: {
      type: 'object',
      properties: {
        id: { type: 'number', example: 111 },
        status: { type: 'number', example: 3, description: '目标状态: 3-取消, 2-结束' }
      },
      required: ['id', 'status']
    }
  })
  @ApiResponse({
    status: 200,
    description: '操作成功',
    schema: {
      properties: {
        code: { type: 'string', example: '200' },
        msg: { type: 'string', example: '会议已取消' }
      }
    }
  })
  async changeStatus(@Body() params: { id: number; status: number }) {
    return this.meetingService.changeMeetingStatus(params);
  }

  @Post('timestatics')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: '获取会议时长统计', description: '统计指定时间范围内各企业的会议预定总时长' })
  @ApiBody({
    schema: {
      type: 'object',
      properties: {
        spaceCode: { type: 'string', example: 'KJY-CD' },
        startDay: { type: 'string', example: '2025-06-06' },
        endDay: { type: 'string', example: '2025-06-06' }
      },
      required: ['spaceCode', 'startDay', 'endDay']
    }
  })
  @ApiResponse({
    status: 200,
    description: '获取成功',
    schema: {
      properties: {
        code: { type: 'string', example: '200' },
        msg: { type: 'string', example: 'success' },
        data: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              orgId: { type: 'number', example: 1 },
              orgName: { type: 'string', example: '成都极企科技有限公司' },
              meetingTime: { type: 'number', example: 3232 }
            }
          }
        }
      }
    }
  })
  async getMeetingTimeStatics(@Body() params: { spaceCode: string; startDay: string; endDay: string }) {
    try {
      const result = await this.meetingService.getMeetingTimeStatics(params);
      return {
        code: '200',
        msg: 'success',
        data: result
      };
    } catch (error) {
      throw new BadRequestException({
        code: '400',
        msg: `获取会议时长统计失败: ${error.message}`
      });
    }
  }
}
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { MeetingController } from './meeting.controller';
import { MeetingService } from './meeting.service';
import { Meeting } from '../entities/Meeting';
import { Floor } from '../entities/Floor';
import { FloorMroom } from '../entities/FloorMroom';
import { Area } from '../entities/Area';
import { User } from '../entities/User';
import { UserRole } from '../entities/UserRole';
import { IotDevice } from '../entities/IotDevice';
import { Org } from '../entities/Org';


@Module({
  imports: [
    TypeOrmModule.forFeature([Meeting, Floor, FloorMroom, Area,User,UserRole,IotDevice,Org]),
  ],
  controllers: [MeetingController],
  providers: [MeetingService],
  exports: [MeetingService],
})
export class MeetingModule {}

import { Injectable, BadRequestException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, LessThanOrEqual, MoreThanOrEqual, Not, LessThan, MoreThan, In } from 'typeorm';
import { Meeting } from '../entities/Meeting';
import { v4 as uuid } from 'uuid';
import { promises as fs } from 'fs';
import { join } from 'path';
import { Floor } from '../entities/Floor';
import { FloorMroom } from '../entities/FloorMroom';
import { Area } from '../entities/Area';
import { User } from '../entities/User';
import { UserRole } from '../entities/UserRole';
import { IotDevice } from '../entities/IotDevice';
import { Org } from '../entities/Org';
import * as moment from 'moment';

// Add the DTOs for the new method
export interface SpaceFloorListDto {
  bookingDate: string;
  spaceCode: string;
  unionid: string;
}

export interface SpaceFloorResponseDto {
  data: {
    list: {
      id: number;
      floorNum: string;
      floorCode: string;
      floorName: string;
      areaCode: string;
      floorSquare: string;
      areaId: string;
      officeArea: string;
      floorArea: string;
      orders: MeetingRoomOrder[];
      meetingRoomId?: string;
      meetingRoomName?: string;
      doors: {
        code: string;
        name: string;
      }[];
    }[];
  };
}

// 添加 order 接口定义
export interface MeetingRoomOrder {
  time: string;
  check: boolean;
  hasOrder: boolean;
  orderTitle: string;
  isTimeFilter: boolean;
  meetingTimeStr?: string;  // 会议时间
  status?: number;          // 会议状态
  statusText?: string;      // 会议状态文字
  bookingId?: string;       // 会议ID，用于识别同一个会议
  meetings?: {
    subject: string;
    time: string;
    status: number;
    statusText: string;
    bookingId: string;
  }[];
}

// DTOs
export interface MeetingScheduleItem {
  startTime: number;
  endTime: number;
  status: number;
  booker: string;
  bookingId: string;
  scheduleId: string;
  meetingSubject: string;
  bookerDept: string;
  bookerName: string;
}

export interface MeetingRoomWithSchedule {
  meetingRoomId: string;
  meetingRoomName: string;
  capacity: number;
  schedule: MeetingScheduleItem[];
}

export interface GetMeetingScheduleParams {
  meetingRoomId?: string;
  startTime?: number;
  endTime?: number;
}

export interface MeetingScheduleResponseData {
  list: MeetingRoomWithSchedule[];
}

export interface ApiResponse<T> {
  code: string;
  msg: string;
  data?: T;
}

// 添加新的接口定义
export interface MeetingItem {
  name: string;
  dept: string;
  status: number;
  startTime: string;
  endTime: string;
}

export interface MeetingRoomWithMeetings {
  roomId: string;
  roomCode: string;
  roomName: string;
  meetingList: MeetingItem[];
}

@Injectable()
export class MeetingService {
  private readonly sceneJsonPath: string;
  logger: any;

  constructor(
    @InjectRepository(Meeting)
    private meetingRepository: Repository<Meeting>,
    @InjectRepository(Floor)
    private floorRepository: Repository<Floor>,
    @InjectRepository(FloorMroom)
    private floorMroomRepository: Repository<FloorMroom>,
    @InjectRepository(Area)
    private areaRepository: Repository<Area>,
    @InjectRepository(User)
    private userRepository: Repository<User>,
    @InjectRepository(UserRole)
    private userRoleRepository: Repository<UserRole>,
    @InjectRepository(IotDevice)
    private deviceRepository: Repository<IotDevice>,
    @InjectRepository(Org)
    private orgRepository: Repository<Org>,
  ) {
    // 根据环境确定文件路径
    const isDevelopment = process.env.NODE_ENV !== 'production';
    this.sceneJsonPath = isDevelopment
      ? join(process.cwd(), 'src', 'server', 'scene', 'data', 'scene.json')
      : join(__dirname, '..', 'scene', 'data', 'scene.json');
    
    // 确保目录存在
    this.ensureDirectoryExists();
  }

  private async ensureDirectoryExists(): Promise<void> {
    try {
      const dirPath = join(this.sceneJsonPath, '..');
      await fs.mkdir(dirPath, { recursive: true });
    } catch (error) {
      console.error(`创建目录失败: ${error.message}`);
    }
  }


  async getMeetingSchedule(params: GetMeetingScheduleParams): Promise<ApiResponse<MeetingScheduleResponseData>> {
    try {
      const { meetingRoomId, startTime, endTime } = params;
      
      // Build query conditions
      const where: any = {};
      
      if (meetingRoomId) {
        where.meetingRoomId = meetingRoomId;
      }
      
      if (startTime && endTime) {
        // Find meetings that overlap with the given time range
        where.startTime = startTime <= endTime ? 
          { lessThanOrEqual: endTime } : 
          { lessThanOrEqual: startTime };
        where.endTime = startTime <= endTime ? 
          { greaterThanOrEqual: startTime } : 
          { greaterThanOrEqual: endTime };
      }
      
      where.status = Not(3); // Exclude canceled meetings

      // Get all meetings matching the criteria
      const meetings = await this.meetingRepository.find({ where });
      
      // Group meetings by room
      const meetingRoomMap = new Map<string, MeetingRoomWithSchedule>();
      
      for (const meeting of meetings) {
        if (!meetingRoomMap.has(meeting.meetingRoomId)) {
          meetingRoomMap.set(meeting.meetingRoomId, {
            meetingRoomId: meeting.meetingRoomId,
            meetingRoomName: meeting.meetingRoomName,
            capacity: meeting.capacity,
            schedule: [],
          });
        }
        
        const roomData = meetingRoomMap.get(meeting.meetingRoomId);
        // Add a null check to satisfy TypeScript
        if (roomData) {
          roomData.schedule.push({
            startTime: meeting.startTime,
            endTime: meeting.endTime,
            status: meeting.status,
            booker: meeting.booker,
            bookingId: meeting.bookingId,
            scheduleId: meeting.scheduleId,
            meetingSubject: meeting.meetingSubject,
            bookerDept: meeting.bookerDept,
            bookerName: meeting.bookerName,
          });
        }
      }
      
      // Convert map to array
      const result: MeetingRoomWithSchedule[] = Array.from(meetingRoomMap.values());
      
      return {
        code: '200',
        msg: 'success',
        data: {
          list: result,
        },
      };
    } catch (error) {
      console.error(`Failed to get meeting schedule: ${error.message}`, error.stack);
      throw new BadRequestException('获取会议日程失败');
    }
  }

  async saveMeetingSchedule(data: MeetingRoomWithSchedule[]): Promise<ApiResponse<null>> {
    try {
      for (const room of data) {
        for (const schedule of room.schedule) {
          // console.log('Saving schedule:', schedule);
          // 检查是新增还是更新
          if (schedule.bookingId === '0') {
            // console.log('Creating new meeting...');
            // 新增操作
            const meeting = this.meetingRepository.create({
              meetingRoomId: room.meetingRoomId,
              meetingRoomName: room.meetingRoomName,
              capacity: room.capacity,
              startTime: schedule.startTime,
              endTime: schedule.endTime,
              status: schedule.status,
              booker: schedule.booker,
              bookingId: uuid(),
              scheduleId: uuid(),
              meetingSubject: schedule.meetingSubject,
              bookerDept: schedule.bookerDept,
              bookerName: schedule.bookerName,
              createTime: Math.floor(Date.now() / 1000).toString(),
            });
            // console.log('Created meeting:', meeting);
            await this.meetingRepository.save(meeting);
          } else {
            // 更新操作
            // 先查找现有记录
            // console.log('Updating existing meeting...');
            const existingMeeting = await this.meetingRepository.findOne({
              where: { bookingId: schedule.bookingId }
            });
            // console.log('Found existing meeting:', existingMeeting);
            if (existingMeeting) {
              // 更新现有记录
              existingMeeting.meetingRoomId = room.meetingRoomId;
              existingMeeting.meetingRoomName = room.meetingRoomName;
              existingMeeting.capacity = room.capacity;
              existingMeeting.startTime = schedule.startTime;
              existingMeeting.endTime = schedule.endTime;
              existingMeeting.status = schedule.status;
              existingMeeting.booker = schedule.booker;
              existingMeeting.scheduleId = schedule.scheduleId;
              existingMeeting.meetingSubject = schedule.meetingSubject;
              existingMeeting.bookerDept = schedule.bookerDept;
              existingMeeting.bookerName = schedule.bookerName;
              
              await this.meetingRepository.save(existingMeeting);
            } else {
              // 如果找不到记录但bookingId不为0，创建新记录
              const meeting = this.meetingRepository.create({
                meetingRoomId: room.meetingRoomId,
                meetingRoomName: room.meetingRoomName,
                capacity: room.capacity,
                startTime: schedule.startTime,
                endTime: schedule.endTime,
                status: schedule.status,
                booker: schedule.booker,
                bookingId: schedule.bookingId,
                scheduleId: schedule.scheduleId,
                meetingSubject: schedule.meetingSubject,
                bookerDept: schedule.bookerDept,
                bookerName: schedule.bookerName,
                createTime: Math.floor(Date.now() / 1000).toString(),
              });
              
              await this.meetingRepository.save(meeting);
            }
          }
        }
      }
      
      return {
        code: '200',
        msg: 'success',
      };
    } catch (error) {
      console.error(`Failed to save meeting schedule: ${error.message}`, error.stack);
      throw new BadRequestException('保存会议日程失败');
    }
  }

  async deleteMeetingSchedule(bookingId: string): Promise<ApiResponse<null>> {
    try {
      console.log('Deleting meeting schedule with bookingId:', bookingId);
      const meeting = await this.meetingRepository.findOne({
        where: { bookingId }
      });
      
      if (!meeting) {
        throw new BadRequestException('会议日程不存在');
      }
      console.log('Deleting meeting:', meeting);
      await this.meetingRepository.delete({ bookingId });
            console.log('Deleting meeting over');

      return {
        code: '200',
        msg: 'success'
      };
    } catch (error) {
      console.error(`Failed to delete meeting schedule: ${error.message}`, error.stack);
      throw new BadRequestException('删除会议日程失败');
    }
  }

  async getMeetingRoomAndOrder(params: SpaceFloorListDto): Promise<SpaceFloorResponseDto> {
    try {
      // 处理日期字符串，转换为时间戳范围
      let startOfDay: number;
      let endOfDay: number;

      try {
        const bookingDate = params.bookingDate || new Date().toISOString().split('T')[0];
        console.log('处理日期:', bookingDate);
        
        // 更灵活的日期格式处理
        let formattedDate = bookingDate;
        
        // 如果日期格式是 YYYY-M-D 或类似格式，转换为 YYYY-MM-DD
        if (/^\d{4}-\d{1,2}-\d{1,2}$/.test(bookingDate)) {
          const [year, month, day] = bookingDate.split('-').map(Number);
          formattedDate = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
          console.log('格式化后的日期:', formattedDate);
        } else if (!/^\d{4}-\d{2}-\d{2}$/.test(bookingDate)) {
          throw new Error(`无效的日期格式: ${bookingDate}`);
        }
        
        const startDate = new Date(`${formattedDate}T00:00:00`);
        const endDate = new Date(`${formattedDate}T23:59:59`);
        
        // 检查日期是否有效
        if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
          throw new Error(`无效的日期: ${bookingDate}`);
        }
        
        startOfDay = Math.floor(startDate.getTime() / 1000);
        endOfDay = Math.floor(endDate.getTime() / 1000);
        
        console.log('时间戳范围:', startOfDay, endOfDay);
      } catch (error) {
        console.error('日期处理错误:', error);
        // 使用当天日期作为后备
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        startOfDay = Math.floor(today.getTime() / 1000);
        
        const todayEnd = new Date();
        todayEnd.setHours(23, 59, 59, 999);
        endOfDay = Math.floor(todayEnd.getTime() / 1000);
        console.log('使用当天日期作为后备:', today.toISOString().split('T')[0]);
        console.log('后备时间戳范围:', startOfDay, endOfDay);
      }

      // 使用联合查询一次性获取所有需要的数据
      const [floors, areas, meetings, meetingRooms, doors] = await Promise.all([
        // 查询楼层数据
        this.floorRepository.find({
          where: { spaceCode: params.spaceCode },
          select: ['id', 'code', 'name', 'areaCode', 'floorArea', 'officeArea'],
          order: { sortOrder: 'ASC' }
        }),
        
        // 查询关联区域数据
        this.areaRepository.find({
          where: { spaceCode: params.spaceCode, deleteFlag: 1 },
          select: ['id', 'code', 'name']
        }),
        
        // 查询当天所有会议预定
        this.meetingRepository.find({
          where: {
            startTime: MoreThanOrEqual(startOfDay),
            endTime: LessThanOrEqual(endOfDay),
            status: Not(3)
          }
        }),
        
        // 查询所有会议室（一次性查询）
        this.floorMroomRepository.find({
          where: { 
            spaceCode: params.spaceCode,
            deleteFlag: 1
          }
        }),
        
        // 查询所有门禁设备（一次性查询）
        this.deviceRepository.find({
          where: { 
            type: 'door',
            spaceCode: params.spaceCode
          }
        })
      ]);

      // 添加默认区域
      areas.unshift({
        id: 0,
        code: '0',
        name: '全部楼层',
        serialNumber: '',
        sortOrder: 0,
        deleteFlag: 0,
        spaceCode: params.spaceCode ? params.spaceCode : '',
        createtime: ''
      });

      // 生成时间段数组（8:00-23:45，每15分钟一条）
      const timeSlots: MeetingRoomOrder[] = [];
      for (let hour = 8; hour <= 23; hour++) {
        // 添加每小时的四个15分钟时间段
        timeSlots.push({
          time: `${hour.toString().padStart(2, '0')}:00`,
          check: false,
          hasOrder: false,
          orderTitle: "",
          isTimeFilter: false
        });
        timeSlots.push({
          time: `${hour.toString().padStart(2, '0')}:15`,
          check: false,
          hasOrder: false,
          orderTitle: "",
          isTimeFilter: false
        });
        timeSlots.push({
          time: `${hour.toString().padStart(2, '0')}:30`,
          check: false,
          hasOrder: false,
          orderTitle: "",
          isTimeFilter: false
        });
        timeSlots.push({
          time: `${hour.toString().padStart(2, '0')}:45`,
          check: false,
          hasOrder: false,
          orderTitle: "",
          isTimeFilter: false
        });
      }

      // 创建索引映射以提高查询效率
      const meetingRoomsByFloor = new Map<string, any[]>();
      const doorsByFloorAndRoom = new Map<string, any[]>();
      const meetingsByRoomId = new Map<string, any[]>();

      // 按楼层分组会议室
      meetingRooms.forEach(room => {
        if (!meetingRoomsByFloor.has(room.floorCode)) {
          meetingRoomsByFloor.set(room.floorCode, []);
        }
        meetingRoomsByFloor.get(room.floorCode)!.push(room);
      });

      // 按楼层和会议室分组门禁设备
      doors.forEach(door => {
        const key = `${door.floorCode}-${door.floorAreaCode}`;
        if (!doorsByFloorAndRoom.has(key)) {
          doorsByFloorAndRoom.set(key, []);
        }
        doorsByFloorAndRoom.get(key)!.push(door);
      });

      // 按会议室ID分组会议
      meetings.forEach(meeting => {
        const roomId = meeting.meetingRoomId;
        if (!meetingsByRoomId.has(roomId)) {
          meetingsByRoomId.set(roomId, []);
        }
        meetingsByRoomId.get(roomId)!.push(meeting);
      });

      // 明确定义 floorResults 的类型
      const floorResults: SpaceFloorResponseDto['data']['list'] = [];
      
      // 处理每个楼层的数据
      for (const floor of floors) {
        const floorMeetingRooms = meetingRoomsByFloor.get(floor.code) || [];
        
        // console.log(`楼层 ${floor.code} 有 ${floorMeetingRooms.length} 个会议室`);

        // 为每个会议室生成时间段数据
        for (const meetingRoom of floorMeetingRooms) {
          // 复制时间段模板
          const roomTimeSlots = JSON.parse(JSON.stringify(timeSlots));
          
          // 获取该会议室的会议
          const roomMeetings = meetingsByRoomId.get(meetingRoom.id.toString()) || [];
          console.log(`会议室 ${meetingRoom.code} 有 ${roomMeetings.length} 个预定`);
          
          // 处理每个会议，更新对应时间段的状态
          for (const meeting of roomMeetings) {
            const meetingStartTime = new Date(meeting.startTime * 1000);
            const meetingEndTime = new Date(meeting.endTime * 1000);
            
            console.log(`处理会议: ${meeting.meetingSubject}, 时间: ${meetingStartTime} - ${meetingEndTime}, ID: ${meeting.bookingId}`);
            
            // 遍历所有时间段，检查是否与会议时间重叠
            for (const slot of roomTimeSlots) {
              const [slotHour, slotMinute] = slot.time.split(':').map(Number);
              const slotStartTime = new Date(meetingStartTime);
              slotStartTime.setHours(slotHour, slotMinute, 0, 0);
              
              const slotEndTime = new Date(slotStartTime);
              slotEndTime.setMinutes(slotEndTime.getMinutes() + 15); // 15分钟时间段
              
              // 检查时间段是否与会议时间重叠
              if (
                (slotStartTime >= meetingStartTime && slotStartTime < meetingEndTime) ||
                (slotEndTime > meetingStartTime && slotEndTime <= meetingEndTime) ||
                (slotStartTime <= meetingStartTime && slotEndTime >= meetingEndTime)
              ) {
                console.log(`时间段 ${slot.time} 与会议重叠`);
                
                slot.hasOrder = true;
                
                // 格式化会议时间
                const formattedStartTime = `${meetingStartTime.getHours().toString().padStart(2, '0')}:${meetingStartTime.getMinutes().toString().padStart(2, '0')}`;
                const formattedEndTime = `${meetingEndTime.getHours().toString().padStart(2, '0')}:${meetingEndTime.getMinutes().toString().padStart(2, '0')}`;
                const meetingTimeStr = `${formattedStartTime}-${formattedEndTime}`;
                
                // 获取会议状态
                const now = Math.floor(Date.now() / 1000);
                let status = 0;
                let statusText = '未开始';
                
                if (meeting.status === 3) {
                  status = 3;
                  statusText = '已取消';
                } else if (meeting.status === 2) {
                  status = 2;
                  statusText = '已结束';
                } else if (now < meeting.startTime) {
                  status = 0;
                  statusText = '未开始';
                } else if (now > meeting.endTime) {
                  status = 2;
                  statusText = '已结束';
                } else {
                  status = 1;
                  statusText = '进行中';
                }
                
                // 设置slot的会议信息
                slot.meetingTimeStr = meetingTimeStr;
                slot.status = status;
                slot.statusText = statusText;
                slot.bookingId = meeting.bookingId;
                slot.orderTitle = meeting.meetingSubject;
                
                // 构建会议信息
                const meetingInfo = {
                  subject: meeting.meetingSubject,
                  time: meetingTimeStr,
                  status,
                  statusText,
                  bookingId: meeting.bookingId
                };
                
                // 将会议信息添加到slot.meetings中
                if (!slot.meetings) {
                  slot.meetings = [];
                }
                slot.meetings.push(meetingInfo);
                
                console.log(`设置时间段 ${slot.time} 的会议信息: ${slot.orderTitle}, ${slot.meetingTimeStr}, ${slot.statusText}`);
              }
            }
          }
          
          // 获取会议室关联的门禁设备
          const roomDoors = doorsByFloorAndRoom.get(`${floor.code}-${meetingRoom.code}`) || [];
          
          // 将会议室数据添加到结果中
          floorResults.push({
            id: meetingRoom.id,
            floorNum: floor.code,
            floorCode: floor.code,
            floorName: floor.name,
            areaCode: floor.areaCode,
            floorSquare: floor.floorArea || '',
            areaId: floor.areaCode,
            officeArea: floor.officeArea || '',
            floorArea: floor.floorArea || '',
            orders: roomTimeSlots,
            meetingRoomId: meetingRoom.code,
            meetingRoomName: meetingRoom.name,
            doors: roomDoors.map(door => ({
              code: door.code,
              name: door.name
            }))
          });
        }
      }
      
      // console.log('返回结果:', floorResults);
      return {
        data: {
          list: floorResults
        }
      };
    } catch (error) {
      console.error('获取会议室和预定信息失败:', error);
      throw new BadRequestException(`获取会议室和预定信息失败: ${error.message}`);
    }
  }

  /**
   * 简化的会议预定方法 - 支持MQTT调用
   * @param params 包含会议室编码、会议时间、主题和用户ID的对象
   * @returns 预定结果
   */
  async saveMeetingScheduleSimple(params: any): Promise<ApiResponse<{ bookingId: string }>> {
    try {
      // 支持两种调用方式：
      // 1. 直接传入四个参数 (从控制器调用)
      // 2. 传入一个包含所有参数的对象 (从MQTT调用)
      
      let meetingRoomCode: string;
      let meetingTime: string;
      let subject: string;
      let unionid: string;
      
      if (typeof params === 'object' && params !== null) {
        // MQTT调用方式，参数是一个对象
        meetingRoomCode = params.meetingRoomCode;
        meetingTime = params.meetingTime;
        subject = params.subject;
        unionid = params.unionid;
      } else {
        // 直接参数调用方式 (这种情况实际上不会发生，因为我们已经修改了方法签名)
        // 保留这段代码是为了向后兼容
        meetingRoomCode = arguments[0] as string;
        meetingTime = arguments[1] as string;
        subject = arguments[2] as string;
        unionid = arguments[3] as string;
      }
      
      console.log(`简化预定会议: 会议室=${meetingRoomCode}, 时间=${meetingTime}, 主题=${subject}, 用户=${unionid}`);
      
      // 参数验证
      if (!meetingRoomCode || !meetingTime || !subject || !unionid) {
        throw new BadRequestException('缺少必要参数: meetingRoomCode, meetingTime, subject, unionid');
      }
      
      // 1. 查询会议室信息
      // 注意：这里使用 code 字段而不是 meetingRoomCode
      const meetingRoom = await this.floorMroomRepository.findOne({
        where: { code: meetingRoomCode, deleteFlag: 1 }
      });
      
      if (!meetingRoom) {
        throw new BadRequestException(`会议室不存在: ${meetingRoomCode}`);
      }
      
      console.log(`找到会议室: ID=${meetingRoom.id}, 名称=${meetingRoom.name}`);
      
      // 2. 解析会议时间
      // 格式: "2025-6-5 22:30-23:00"
      const timeRegex = /^(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{1,2})-(\d{1,2}):(\d{1,2})$/;
      const match = meetingTime.match(timeRegex);
      
      if (!match) {
        throw new BadRequestException(`无效的会议时间格式: ${meetingTime}, 正确格式为 "YYYY-M-D HH:MM-HH:MM"`);
      }
      
      const [_, yearStr, monthStr, dayStr, startHourStr, startMinuteStr, endHourStr, endMinuteStr] = match;
      
      // 转换为数字
      const year = parseInt(yearStr, 10);
      const month = parseInt(monthStr, 10);
      const day = parseInt(dayStr, 10);
      const startHour = parseInt(startHourStr, 10);
      const startMinute = parseInt(startMinuteStr, 10);
      const endHour = parseInt(endHourStr, 10);
      const endMinute = parseInt(endMinuteStr, 10);
      
      // 格式化日期，确保月份和日期有两位数
      const formattedDate = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
      
      // 创建开始和结束时间的Date对象
      const startDate = new Date(`${formattedDate}T${startHour.toString().padStart(2, '0')}:${startMinute.toString().padStart(2, '0')}:00`);
      const endDate = new Date(`${formattedDate}T${endHour.toString().padStart(2, '0')}:${endMinute.toString().padStart(2, '0')}:00`);
      
      // 检查日期是否有效
      if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
        throw new BadRequestException(`无效的日期时间: ${meetingTime}`);
      }
      
      // 转换为时间戳
      const startTime = Math.floor(startDate.getTime() / 1000);
      const endTime = Math.floor(endDate.getTime() / 1000);
      
      console.log(`会议时间: 开始=${new Date(startTime * 1000).toISOString()}, 结束=${new Date(endTime * 1000).toISOString()}`);
      
      // 3. 查询用户信息
      const user = await this.userRepository.findOne({ where: { unionid } });
      
      if (!user) {
        throw new BadRequestException(`用户不存在: ${unionid}`);
      }
      
      console.log(`找到用户: ID=${user.userId}, 姓名=${user.realName}, 部门=${user.departmentId}`);
      
      // 4. 检查时间段是否已被预定
      const existingMeetings = await this.meetingRepository.find({
        where: [
          {
            meetingRoomId: meetingRoom.id.toString(),
            startTime: LessThan(endTime),  // 使用 LessThan 而不是 LessThanOrEqual
            endTime: MoreThan(startTime),  // 使用 MoreThan 而不是 MoreThanOrEqual
            status: Not(3)
          }
        ]
      });
      
      if (existingMeetings.length > 0) {
        console.log(`发现时间冲突: ${existingMeetings.length} 个会议`);
        for (const meeting of existingMeetings) {
          console.log(`冲突会议: ${meeting.meetingSubject}, 时间: ${new Date(meeting.startTime * 1000)} - ${new Date(meeting.endTime * 1000)}`);
        }
        throw new BadRequestException('该时间段已被预定');
      }
      
      // 5. 创建会议预定
      const bookingId = uuid();
      const meeting = this.meetingRepository.create({
        meetingRoomId: meetingRoom.id.toString(),
        meetingRoomName: meetingRoom.name,
        capacity:  0,
        startTime,
        endTime,
        status: 0, // 假设 0 表示正常状态
        booker: user.userId.toString(),
        bookingId,
        scheduleId: uuid(),
        meetingSubject: subject,
        bookerDept: user.departmentId ? user.departmentId.toString() : '',
        bookerName: user.realName || '',
        createTime: Math.floor(Date.now() / 1000).toString(),
      });
      
      await this.meetingRepository.save(meeting);
      
      console.log(`会议预定成功: bookingId=${bookingId}`);
      
      return {
        code: '200',
        msg: 'success',
        data: { bookingId }
      };
    } catch (error) {
      console.error(`会议预定失败: ${error.message}`, error.stack);
      throw new BadRequestException(`会议预定失败: ${error.message}`);
    }
  }

  /**
   * 获取指定日期的会议列表
   * @param day 日期字符串，格式为 YYYY-MM-DD
   * @returns 会议室及其会议列表
   */
  async getMeetingList(day: string): Promise<MeetingRoomWithMeetings[]> {
    try {
      // 处理日期字符串，转换为时间戳范围
      let startOfDay: number;
      let endOfDay: number;

      try {
        // 更灵活的日期格式处理
        let formattedDate = day;
        
        // 如果日期格式是 YYYY-M-D 或类似格式，转换为 YYYY-MM-DD
        if (/^\d{4}-\d{1,2}-\d{1,2}$/.test(day)) {
          const [year, month, dayNum] = day.split('-').map(Number);
          formattedDate = `${year}-${month.toString().padStart(2, '0')}-${dayNum.toString().padStart(2, '0')}`;
          // console.log('格式化后的日期:', formattedDate);
        } else if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) {
          throw new Error(`无效的日期格式: ${day}`);
        }
        
        const startDate = new Date(`${formattedDate}T00:00:00`);
        const endDate = new Date(`${formattedDate}T23:59:59`);
        
        // 检查日期是否有效
        if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
          throw new Error(`无效的日期: ${day}`);
        }
        
        startOfDay = Math.floor(startDate.getTime() / 1000);
        endOfDay = Math.floor(endDate.getTime() / 1000);
        
        // console.log('时间戳范围:', startOfDay, endOfDay);
      } catch (error) {
        console.error('日期处理错误:', error);
        throw new BadRequestException(`日期格式错误: ${error.message}`);
      }
      
      // 查询当天所有会议预定
      const meetings = await this.meetingRepository.find({
        where: {
          startTime: MoreThanOrEqual(startOfDay),
          endTime: LessThanOrEqual(endOfDay),
          status: Not(3)
        }
      });
      
      // console.log(`找到 ${meetings.length} 个会议预定`);
      
      // 获取所有相关的会议室
      const meetingRoomIds = [...new Set(meetings.map(m => m.meetingRoomId))];
      
      // 创建结果映射
      const meetingRoomsMap = new Map<string, MeetingRoomWithMeetings>();
      
      // 查询所有相关会议室的详细信息
      for (const roomId of meetingRoomIds) {
        const meetingRoom = await this.floorMroomRepository.findOne({
          where: { id: parseInt(roomId), deleteFlag: 1 }
        });
        
        if (meetingRoom) {
          meetingRoomsMap.set(roomId, {
            roomId: roomId,
            roomCode: meetingRoom.code,
            roomName: meetingRoom.name,
            meetingList: []
          });
        }
      }
      
      // 获取当前时间
      const now = Math.floor(Date.now() / 1000);
      
      // 处理每个会议，添加到对应会议室的列表中
      for (const meeting of meetings) {
        const roomData = meetingRoomsMap.get(meeting.meetingRoomId);
        
        if (roomData) {
          // 确定会议状态
          let status: number;
          if (meeting.startTime > now) {
            status = 0; // 未开始
          } else if (meeting.endTime < now) {
            continue; // 已结束的会议不显示
          } else {
            status = 1; // 进行中
          }
          
          // 格式化时间
          const startDate = new Date(meeting.startTime * 1000);
          const endDate = new Date(meeting.endTime * 1000);
          
          const startTimeStr = `${startDate.getHours().toString().padStart(2, '0')}:${startDate.getMinutes().toString().padStart(2, '0')}`;
          const endTimeStr = `${endDate.getHours().toString().padStart(2, '0')}:${endDate.getMinutes().toString().padStart(2, '0')}`;
          
          // 添加会议信息
          roomData.meetingList.push({
            name: meeting.bookerName || '',
            dept: meeting.bookerDept || '',
            status,
            startTime: startTimeStr,
            endTime: endTimeStr
          });
        }
      }
      
      // 对每个会议室的会议列表按开始时间排序
      for (const roomData of meetingRoomsMap.values()) {
        roomData.meetingList.sort((a, b) => {
          const aTime = a.startTime.split(':').map(Number);
          const bTime = b.startTime.split(':').map(Number);
          
          // 比较小时
          if (aTime[0] !== bTime[0]) {
            return aTime[0] - bTime[0];
          }
          
          // 如果小时相同，比较分钟
          return aTime[1] - bTime[1];
        });
      }
      
      // 转换为数组并返回
      return Array.from(meetingRoomsMap.values());
    } catch (error) {
      console.error('获取会议列表失败:', error);
      throw new BadRequestException(`获取会议列表失败: ${error.message}`);
    }
  }

  /**
   * 获取用户预定的会议
   * @param params 包含用户ID、楼层编码和空间编码的参数
   * @returns 用户预定的会议列表
   */
  async getUserMeetingOrders(params: { userId: number; floorCode: string; spaceCode: string }): Promise<any[]> {
    try {
      const { userId, floorCode, spaceCode } = params;
      let isAdmin = false;
      // 检查用户是否是管理员
      if (userId === 1) {
        isAdmin = true;
      } else {
        const userRoles = await this.userRoleRepository.find({
          where: { userId: userId.toString() }
        });
        
        isAdmin = userRoles.some(role => role.roleCode === 'admin');
      }
 
      // console.log(`用户 ${userId} 是否为管理员: ${isAdmin}`);
      
      // 创建查询构建器
      const query = this.meetingRepository.createQueryBuilder('meeting');
      
      // 如果不是管理员，则只查询该用户预定的会议
      if (!isAdmin) {
        query.where('meeting.booker = :userId', { userId: userId.toString() });
      }
      
      // 如果floorCode不是'all'，需要查询特定楼层的会议室
      if (floorCode !== 'all') {
        // 先获取该楼层的所有会议室ID
        const meetingRooms = await this.floorMroomRepository.find({
          where: { 
            spaceCode: spaceCode,
            floorCode: floorCode,
            deleteFlag: 1
          },
          select: ['id']
        });
        
        const meetingRoomIds = meetingRooms.map(room => room.id.toString());
        
        if (meetingRoomIds.length > 0) {
          // 如果已经有where条件，使用andWhere，否则使用where
          if (!isAdmin) {
            query.andWhere('meeting.meetingRoomId IN (:...meetingRoomIds)', { meetingRoomIds });
          } else {
            query.where('meeting.meetingRoomId IN (:...meetingRoomIds)', { meetingRoomIds });
          }
        } else {
          // 如果没有找到会议室，返回空数组
          return [];
        }
      } else {
        // 查询该空间的所有会议室
        const meetingRooms = await this.floorMroomRepository.find({
          where: { 
            spaceCode: spaceCode,
            deleteFlag: 1
          },
          select: ['id']
        });
        
        const meetingRoomIds = meetingRooms.map(room => room.id.toString());
        
        if (meetingRoomIds.length > 0) {
          // 如果已经有where条件，使用andWhere，否则使用where
          if (!isAdmin) {
            query.andWhere('meeting.meetingRoomId IN (:...meetingRoomIds)', { meetingRoomIds });
          } else {
            query.where('meeting.meetingRoomId IN (:...meetingRoomIds)', { meetingRoomIds });
          }
        } else {
          // 如果没有找到会议室，返回空数组
          return [];
        }
      }
      
      // 按开始时间排序（从近到远）
      query.orderBy('meeting.startTime', 'DESC');
      
      // 执行查询
      const meetings = await query.getMany();
      
      // 创建会议室ID到楼层的映射
      const roomFloorMap = new Map<string, string>();
      
      // 获取所有相关会议室的楼层信息
      const meetingRoomIds = [...new Set(meetings.map(m => m.meetingRoomId))];
      for (const roomId of meetingRoomIds) {
        const meetingRoom = await this.floorMroomRepository.findOne({
          where: { id: parseInt(roomId), deleteFlag: 1 },
          select: ['id', 'floorCode']
        });
        
        if (meetingRoom) {
          roomFloorMap.set(roomId, meetingRoom.floorCode);
        }
      }
      
      // 返回结果，包含会议室所在楼层
      return meetings.map(meeting => ({
        id: meeting.id,
        meetingRoomId: meeting.meetingRoomId,
        meetingRoomName: meeting.meetingRoomName,
        floorCode: roomFloorMap.get(meeting.meetingRoomId) || '',
        startTime: meeting.startTime,
        status: this.getMeetingStatus(meeting.startTime, meeting.endTime, meeting.status)[0],
        statusName: this.getMeetingStatus(meeting.startTime, meeting.endTime, meeting.status)[1],
        endTime: meeting.endTime,
        meetingSubject: meeting.meetingSubject,
        bookingId: meeting.bookingId,
        booker: meeting.booker,
        bookerName: meeting.bookerName,
        bookerDept: meeting.bookerDept
      }));
    } catch (error) {
      this.logger.error(`获取用户会议预定失败: ${error.message}`, error.stack);
      throw new Error(`获取用户会议预定失败: ${error.message}`);
    }
  }

  /**
   * 通过用户unionid获取用户预定的会议
   * @param params 包含用户unionid、楼层编码和空间编码的参数
   * @returns 用户预定的会议列表
   */
  async getUserMeetingOrdersByUid(params: { uid: string; floorCode: string; spaceCode: string }): Promise<any> {
    try {
      const { uid, floorCode, spaceCode } = params;
      
      // 通过unionid查询用户ID
      const user = await this.userRepository.findOne({
        where: { unionid: uid, deleteFlag: 1 }
      });
      
      if (!user) {
        console.warn(`未找到用户: unionid=${uid}`);
        throw new Error('未找到用户');
      }
      
      console.log(`找到用户: userId=${user.userId}, unionid=${uid}`);
      
      // 调用现有方法获取用户会议预定
      const meetings = await this.getUserMeetingOrders({
        userId: user.userId,
        floorCode,
        spaceCode
      });
      
      // 按照 getMeetingRoomAndOrder 的格式返回数据
      return {
        code: '200',
        msg: 'success',
        data: {
          list: meetings.map(meeting => ({
            id: meeting.id,
            meetingRoomId: meeting.meetingRoomId,
            meetingRoomName: meeting.meetingRoomName,
            startTime: meeting.startTime,
            endTime: meeting.endTime,
            meetingTime: `${moment.unix(meeting.startTime).format("YYYY-MM-DD HH:mm")} - ${moment.unix(meeting.endTime).format("HH:mm")}`,
            meetingSubject: meeting.meetingSubject,
            status: meeting.status,
            statusName: meeting.statusName,
            floorCode: meeting.floorCode,
            bookingId: meeting.bookingId,
            bookerName: user.realName || '',
            bookerDept: user.departmentId ? user.departmentId.toString() : ''
          }))
        }
      };
    } catch (error) {
      console.error(`通过unionid获取用户会议预定失败: ${error.message}`, error.stack);
      return {
        code: '400',
        msg: `获取用户会议预定失败: ${error.message}`,
        data: {
          list: []
        }
      };
    }
  }

  /**
   * 获取会议状态
   * @param startTime 会议开始时间
   * @param endTime 会议结束时间
   * @returns 会议状态：0-未开始，1-进行中，2-已结束，3-已取消
   */
  private getMeetingStatus(startTime: number, endTime: number,status: number): (string | number)[] {
    const now = Math.floor(Date.now() / 1000);
    let returnObj = [0, '未开始'];
    if(status==3){
      returnObj[0] = 3; // 已取消
      returnObj[1] = '已取消';
    }else if(status==2){
      returnObj[0] = 2; // 已结束
      returnObj[1] = '已结束';
    }else{
        if (now < startTime) {
          returnObj[0] = 0; // 未开始
          returnObj[1] = '未开始';
        } else if (now > endTime) {
          returnObj[0] = 2; // 已结束
          returnObj[1] = '已结束';
        } else {
          returnObj[0] = 1; // 进行中
          returnObj[1] = '进行中';
        }
    }
    return returnObj;
  }

  /**
   * 修改会议状态
   * @param params 包含会议ID和目标状态的参数
   * @returns 操作结果
   */
  async changeMeetingStatus(params: { id: number; status: number }): Promise<ApiResponse<any>> {
    try {
      const { id, status } = params;
      
      // 查找会议
      const meeting = await this.meetingRepository.findOne({
        where: { id }
      });
      
      if (!meeting) {
        throw new BadRequestException('会议不存在');
      }
      
      // 获取当前会议状态
      // const currentStatus = this.getMeetingStatus(meeting.startTime, meeting.endTime)[0];
      
      // 根据当前状态和目标状态执行不同操作
      if (status === 0) {
        console.log('未开始的会议，执行取消操作',meeting.id);
        // 未开始的会议，执行取消操作
        meeting.status = 3; // 取消状态
        await this.meetingRepository.save(meeting);
        console.log('会议已取消',meeting);

        return {
          code: '200',
          msg: '会议已取消',
          data: meeting
        };
      } else if (status === 1) {
        // 进行中的会议，执行结束操作
        meeting.status = 2; // 已结束状态
        meeting.endTime = Math.floor(Date.now() / 1000); // 更新结束时间为当前时间
        await this.meetingRepository.save(meeting);
        
        return {
          code: '200',
          msg: '会议已结束',
          data: meeting
        };
      } else {
        throw new BadRequestException('无效的状态变更操作');
      }
    } catch (error) {
      console.error(`修改会议状态失败: ${error.message}`, error.stack);
      throw new BadRequestException(`修改会议状态失败: ${error.message}`);
    }
  }

  /**
   * 检查用户是否有会议室门禁权限
   * @param params 包含路径信息和用户ID的参数
   * @returns 是否有权限
   */
  async checkMeetingRoomDoorAccess(params: {
    spaceCode: string;
    floorAreaCode: string;
    floorCode: string;
    areaCode: string;
    userId: string;
  }): Promise<boolean> {
    try {
      const { spaceCode, floorAreaCode, floorCode, areaCode, userId } = params;
      
      // 查找对应的会议室
      const meetingRoom = await this.floorMroomRepository.findOne({
        where: {
          spaceCode,
          code: areaCode,
          floorCode,
          areaCode: floorAreaCode,
          deleteFlag: 1
        }
      });
      
      if (!meetingRoom) {
        return false;
      }
      
      // 计算当前时间和提前5分钟的时间
      const now = Math.floor(Date.now() / 1000);
      const fiveMinutesInSeconds = 5 * 60;
      
      // 查询该用户在该会议室的预约
      const meeting = await this.meetingRepository.findOne({
        where: {
          meetingRoomId: meetingRoom.id.toString(),
          booker: userId,
          startTime: LessThanOrEqual(now + fiveMinutesInSeconds),
          endTime: MoreThanOrEqual(now),
          status: Not(3) // 排除已取消的会议
        }
      });
      
      return !!meeting; // 如果找到会议预约，返回true，否则返回false
    } catch (error) {
      console.error(`检查会议室门禁权限失败: ${error.message}`, error.stack);
      return false;
    }
  }

  /**
   * 获取会议时长统计
   * @param params 包含空间编码和时间范围的参数
   * @returns 各企业的会议预定总时长统计
   */
  async getMeetingTimeStatics(params: { spaceCode: string; startDay: string; endDay: string }): Promise<any[]> {
    try {
      const { spaceCode, startDay, endDay } = params;
      
      // 处理日期字符串，转换为时间戳范围
      let startOfDay: number;
      let endOfDay: number;

      try {
        // 处理开始日期
        const startDate = new Date(startDay);
        startDate.setHours(0, 0, 0, 0);
        startOfDay = Math.floor(startDate.getTime() / 1000);
        
        // 处理结束日期
        const endDate = new Date(endDay);
        endDate.setHours(23, 59, 59, 999);
        endOfDay = Math.floor(endDate.getTime() / 1000);
        
        console.log(`时间戳范围: ${startOfDay} - ${endOfDay}`);
      } catch (error) {
        console.error('日期处理错误:', error);
        throw new Error(`日期格式错误: ${error.message}`);
      }
      
      // 查询该空间的所有会议室
      const meetingRooms = await this.floorMroomRepository.find({
        where: { 
          spaceCode: spaceCode,
          deleteFlag: 1
        },
        select: ['id']
      });
      
      const meetingRoomIds = meetingRooms.map(room => room.id.toString());
      
      if (meetingRoomIds.length === 0) {
        // 如果没有找到会议室，返回空数组
        return [{
          orgId: 0,
          orgName: '全部企业',
          meetingTime: 0,
          bookingNum: 0
        }];
      }
      
      // 查询时间范围内的所有会议（排除已取消的）
      const meetings = await this.meetingRepository.find({
        where: {
          meetingRoomId: In(meetingRoomIds),
          startTime: MoreThanOrEqual(startOfDay),
          endTime: LessThanOrEqual(endOfDay),
          status: Not(3) // 排除已取消的会议
        }
      });
      
      console.log(`找到 ${meetings.length} 个会议预定`);
      
      // 计算总时长（分钟）
      let totalMinutes = 0;
      
      // 按企业ID分组的时长统计
      const orgTimeMap = new Map<number, number>();
      
      // 按企业ID分组的预定次数统计
      const orgCountMap = new Map<number, number>();
      
      // 用户ID到企业ID的映射
      const userOrgMap = new Map<string, number>();
      
      // 企业ID到企业名称的映射
      const orgNameMap = new Map<number, string>();
      
      // 处理每个会议
      for (const meeting of meetings) {
        // 计算会议时长（分钟）
        const durationMinutes = Math.floor((meeting.endTime - meeting.startTime) / 60);
        totalMinutes += durationMinutes;
        
        // 获取预定者的企业ID
        let orgId: number;
        
        // 检查是否已经有该用户的企业ID缓存
        if (userOrgMap.has(meeting.booker)) {
          orgId = userOrgMap.get(meeting.booker)!;
        } else {
          // 查询用户信息
          const user = await this.userRepository.findOne({
            where: { userId: parseInt(meeting.booker) },
            select: ['userId', 'orgId']
          });
          
          if (user && user.orgId) {
            orgId = user.orgId;
            userOrgMap.set(meeting.booker, orgId);
            
          } else {
            // 如果找不到用户或企业ID，使用默认值
            orgId = 0;
            userOrgMap.set(meeting.booker, 0);
          }
        }
        
        // 更新企业时长统计
        if (orgTimeMap.has(orgId)) {
          orgTimeMap.set(orgId, orgTimeMap.get(orgId)! + durationMinutes);
          orgCountMap.set(orgId, orgCountMap.get(orgId)! + 1);
        } else {
          orgTimeMap.set(orgId, durationMinutes);
          orgCountMap.set(orgId, 1);
        }
      }
      
      // 如果没有企业名称缓存，查询企业信息
      for (const orgId of orgTimeMap.keys()) {
        if (orgId > 0 && !orgNameMap.has(orgId)) {
          const org = await this.orgRepository.findOne({
            where: { id: orgId },
            select: ['id', 'orgName']
          });
          
          if (org) {
            orgNameMap.set(orgId, org.orgName);
          } else {
            orgNameMap.set(orgId, `企业${orgId}`);
          }
        }
      }
      
      // 构建结果数组
      const result: { orgId: number; orgName: string; meetingTime: number; bookingNum: number }[] = [];
      
      // 添加总计
      result.push({
        orgId: 0,
        orgName: '全部企业',
        meetingTime: totalMinutes,
        bookingNum: meetings.length
      });
      
      // 添加各企业统计
      for (const [orgId, minutes] of orgTimeMap.entries()) {
        if (orgId > 0) { // 排除默认值
          result.push({
            orgId,
            orgName: orgNameMap.get(orgId) || `企业${orgId}`,
            meetingTime: minutes,
            bookingNum: orgCountMap.get(orgId) || 0
          });
        }
      }
      
      // 按会议时长降序排序
      result.sort((a, b) => {
        if (a.orgId === 0) return -1; // 总计始终排在第一位
        if (b.orgId === 0) return 1;
        return b.meetingTime - a.meetingTime;
      });
      
      return result;
    } catch (error) {
      console.error(`获取会议时长统计失败: ${error.message}`, error.stack);
      throw new Error(`获取会议时长统计失败: ${error.message}`);
    }
  }
}

import { ApiProperty } from "@nestjs/swagger";

export class SaveMeetingScheduleSimpleDto {
  @ApiProperty({ description: '会议室编码', example: 'M1001' })
  meetingRoomCode: string;

  @ApiProperty({ description: '会议时间，格式如 "2025-6-5 22:30-23:00"', example: '2025-6-5 22:30-23:00' })
  meetingTime: string;

  @ApiProperty({ description: '会议主题', example: '何铮预定的会议' })
  subject: string;

  @ApiProperty({ description: '用户的unionid', example: 'xxxxx' })
  unionid: string;
}
```

