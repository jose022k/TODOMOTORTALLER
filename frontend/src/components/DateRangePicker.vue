<template>
  <div class="drp" ref="drp">
    <button class="drp-trigger" @click="toggle" :class="{ active: isOpen }">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
      <span class="drp-label">{{ displayLabel }}</span>
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" class="drp-chevron" :class="{ open: isOpen }"><polyline points="6 9 12 15 18 9"/></svg>
    </button>

    <transition name="drp-pop">
      <div v-if="isOpen" class="drp-dropdown">
        <div class="drp-quick">
          <button v-for="q in quickOptions" :key="q.label" class="drp-quick-btn" :class="{ selected: isQuickSelected(q) }" @click="applyQuick(q)">{{ q.label }}</button>
        </div>

        <div class="drp-calendars">
          <!-- Left calendar -->
          <div class="drp-month">
            <div class="drp-month-header">
              <button class="drp-nav" @click="navLeftPrev"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg></button>
              <span class="drp-month-title">{{ monthLabel(leftYear, leftMonth) }}</span>
              <button class="drp-nav" @click="navLeftNext" :disabled="isLeftNextDisabled"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg></button>
            </div>
            <div class="drp-weekdays">
              <span v-for="d in weekdays" :key="d">{{ d }}</span>
            </div>
            <div class="drp-days">
              <button v-for="(day, i) in leftDays" :key="i" class="drp-day" :class="dayClass(day)" :disabled="!day.date" @click="day.date && selectDay(day)">{{ day.label }}</button>
            </div>
          </div>

          <!-- Right calendar -->
          <div class="drp-month">
            <div class="drp-month-header">
              <button class="drp-nav" @click="navRightPrev" :disabled="isRightPrevDisabled"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg></button>
              <span class="drp-month-title">{{ monthLabel(rightYear, rightMonth) }}</span>
              <button class="drp-nav" @click="navRightNext"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg></button>
            </div>
            <div class="drp-weekdays">
              <span v-for="d in weekdays" :key="d">{{ d }}</span>
            </div>
            <div class="drp-days">
              <button v-for="(day, i) in rightDays" :key="i" class="drp-day" :class="dayClass(day)" :disabled="!day.date" @click="day.date && selectDay(day)">{{ day.label }}</button>
            </div>
          </div>
        </div>

        <div class="drp-actions">
          <button class="drp-btn-clear" @click="clear">Limpiar</button>
          <button class="drp-btn-apply" @click="apply">Aplicar</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: "DateRangePicker",
  props: {
    start: { type: String, default: "" },
    end: { type: String, default: "" },
  },
  emits: ["update:start", "update:end", "change"],
  data() {
    const now = new Date();
    return {
      isOpen: false,
      leftYear: now.getFullYear(),
      leftMonth: now.getMonth(),
      rightYear: now.getFullYear(),
      rightMonth: now.getMonth() + 1 > 11 ? 0 : now.getMonth() + 1,
      tempStart: this.start,
      tempEnd: this.end,
      hoverDate: "",
      quickOptions: [
        { label: "Hoy", days: 0 },
        { label: "Esta semana", days: 6 },
        { label: "Este mes", days: 29 },
        { label: "Últimos 7 días", days: 6, offset: true },
        { label: "Últimos 30 días", days: 29, offset: true },
      ],
      weekdays: ["Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do"],
    };
  },
  computed: {
    leftDays() {
      return this.buildDays(this.leftYear, this.leftMonth);
    },
    rightDays() {
      return this.buildDays(this.rightYear, this.rightMonth);
    },
    isLeftNextDisabled() {
      return this.leftYear === this.rightYear && this.leftMonth === this.rightMonth;
    },
    isRightPrevDisabled() {
      return this.leftYear === this.rightYear && this.leftMonth === this.rightMonth;
    },
    displayLabel() {
      if (this.start && this.end) {
        return this.formatShort(this.start) + " – " + this.formatShort(this.end);
      }
      if (this.start) return "Desde " + this.formatShort(this.start);
      if (this.end) return "Hasta " + this.formatShort(this.end);
      return "Seleccionar rango";
    },
  },
  methods: {
    toggle() {
      this.isOpen = !this.isOpen;
      if (this.isOpen) {
        this.tempStart = this.start;
        this.tempEnd = this.end;
        if (this.start) {
          const d = new Date(this.start + "T00:00:00");
          this.leftYear = d.getFullYear();
          this.leftMonth = d.getMonth();
          this.calcRightFromLeft();
        }
      }
    },
    calcRightFromLeft() {
      this.rightMonth = this.leftMonth + 1;
      this.rightYear = this.leftYear;
      if (this.rightMonth > 11) {
        this.rightMonth = 0;
        this.rightYear++;
      }
    },
    navLeftPrev() {
      if (this.leftMonth === 0) {
        this.leftMonth = 11;
        this.leftYear--;
      } else {
        this.leftMonth--;
      }
      this.syncRightAfterLeft();
    },
    navLeftNext() {
      if (this.isLeftNextDisabled) return;
      if (this.leftMonth === 11) {
        this.leftMonth = 0;
        this.leftYear++;
      } else {
        this.leftMonth++;
      }
    },
    navRightPrev() {
      if (this.isRightPrevDisabled) return;
      if (this.rightMonth === 0) {
        this.rightMonth = 11;
        this.rightYear--;
      } else {
        this.rightMonth--;
      }
    },
    navRightNext() {
      if (this.rightMonth === 11) {
        this.rightMonth = 0;
        this.rightYear++;
      } else {
        this.rightMonth++;
      }
    },
    syncRightAfterLeft() {
      const lm = this.leftYear * 12 + this.leftMonth;
      const rm = this.rightYear * 12 + this.rightMonth;
      if (rm <= lm) {
        this.rightMonth = this.leftMonth + 1;
        this.rightYear = this.leftYear;
        if (this.rightMonth > 11) {
          this.rightMonth = 0;
          this.rightYear++;
        }
      }
    },
    buildDays(year, month) {
      const first = new Date(year, month, 1);
      const lastDay = new Date(year, month + 1, 0).getDate();
      let startDow = first.getDay();
      if (startDow === 0) startDow = 6;
      else startDow--;
      const days = [];
      for (let i = 0; i < startDow; i++) days.push({ label: "", date: "" });
      for (let d = 1; d <= lastDay; d++) {
        const mm = String(month + 1).padStart(2, "0");
        const dd = String(d).padStart(2, "0");
        days.push({ label: d, date: `${year}-${mm}-${dd}` });
      }
      return days;
    },
    monthLabel(year, month) {
      const d = new Date(year, month);
      return d.toLocaleDateString("es-ES", { month: "long", year: "numeric" });
    },
    selectDay(day) {
      if (!this.tempStart || (this.tempStart && this.tempEnd)) {
        this.tempStart = day.date;
        this.tempEnd = "";
        this.hoverDate = "";
      } else {
        if (day.date < this.tempStart) {
          this.tempEnd = this.tempStart;
          this.tempStart = day.date;
        } else {
          this.tempEnd = day.date;
        }
        this.autoNavigate(day.date);
      }
    },
    autoNavigate(dateStr) {
      const d = new Date(dateStr + "T00:00:00");
      const y = d.getFullYear();
      const m = d.getMonth();
      const leftM = this.leftYear * 12 + this.leftMonth;
      const rightM = this.rightYear * 12 + this.rightMonth;
      const clickedM = y * 12 + m;
      if (clickedM < leftM) {
        this.leftYear = y;
        this.leftMonth = m;
        this.calcRightFromLeft();
      } else if (clickedM > rightM) {
        this.rightYear = y;
        this.rightMonth = m;
      }
    },
    dayClass(day) {
      if (!day.date) return {};
      const s = this.tempStart;
      const e = this.tempEnd || this.hoverDate;
      const inRange = s && e && day.date > s && day.date < e;
      const isStart = day.date === s;
      const isEnd = day.date === (this.tempEnd || this.hoverDate);
      return {
        "is-start": isStart,
        "is-end": isEnd && s !== e,
        "in-range": inRange || (isStart && isEnd),
        "is-hover": !this.tempEnd && this.hoverDate && day.date === this.hoverDate,
      };
    },
    formatShort(f) {
      const d = new Date(f + "T00:00:00");
      return d.toLocaleDateString("es-ES", { day: "numeric", month: "short", year: "numeric" });
    },
    isQuickSelected(q) {
      if (q.offset) return false;
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const s = this.tempStart ? new Date(this.tempStart + "T00:00:00") : null;
      const e = this.tempEnd ? new Date(this.tempEnd + "T00:00:00") : null;
      if (!s || !e) return false;
      const diff = Math.round((e - s) / 86400000);
      if (q.days === 0) return diff === 0 && this.toStr(s) === this.toStr(today);
      if (q.days === 6) {
        const dow = today.getDay();
        const mon = new Date(today);
        mon.setDate(mon.getDate() - ((dow + 6) % 7));
        return this.toStr(s) === this.toStr(mon) && diff === 6;
      }
      if (q.days === 29) {
        return s.getDate() === 1 && e.getMonth() === today.getMonth() && e.getFullYear() === today.getFullYear() && diff >= 27;
      }
      return false;
    },
    toStr(d) {
      return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
    },
    applyQuick(q) {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const end = new Date(today);
      let start;
      if (q.offset) {
        end.setDate(today.getDate());
        start = new Date(today);
        start.setDate(today.getDate() - q.days);
      } else if (q.days === 0) {
        start = new Date(today);
      } else if (q.days === 6) {
        const dow = today.getDay();
        start = new Date(today);
        start.setDate(today.getDate() - ((dow + 6) % 7));
      } else if (q.days === 29) {
        start = new Date(today.getFullYear(), today.getMonth(), 1);
        end.setFullYear(today.getFullYear(), today.getMonth() + 1, 0);
      }
      this.tempStart = this.toStr(start);
      this.tempEnd = this.toStr(end);
      this.leftYear = start.getFullYear();
      this.leftMonth = start.getMonth();
      this.calcRightFromLeft();
    },
    clear() {
      this.tempStart = "";
      this.tempEnd = "";
      this.$emit("update:start", "");
      this.$emit("update:end", "");
      this.$emit("change");
      this.isOpen = false;
    },
    apply() {
      this.$emit("update:start", this.tempStart);
      this.$emit("update:end", this.tempEnd);
      this.$emit("change");
      this.isOpen = false;
    },
    handleClickOutside(e) {
      if (this.$refs.drp && !this.$refs.drp.contains(e.target)) {
        this.isOpen = false;
      }
    },
  },
  mounted() {
    document.addEventListener("mousedown", this.handleClickOutside);
  },
  beforeUnmount() {
    document.removeEventListener("mousedown", this.handleClickOutside);
  },
  watch: {
    start(v) { this.tempStart = v; },
    end(v) { this.tempEnd = v; },
  },
};
</script>

<style scoped>
.drp { position: relative; display: inline-block; }

.drp-trigger {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #fff;
  border: 1.5px solid #d1d5db;
  border-radius: 10px;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 600;
  color: #1a1a1a;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
  white-space: nowrap;
  font-family: inherit;
}
.drp-trigger:hover { border-color: #94a3b8; }
.drp-trigger.active {
  border-color: #ffaa00;
  box-shadow: 0 0 0 3px rgba(255,170,0,0.12);
}
.drp-label { color: #475569; }
.drp-trigger.active .drp-label,
.drp-trigger:hover .drp-label { color: #1a1a1a; }

.drp-chevron {
  transition: transform 0.2s;
  color: #94a3b8;
}
.drp-chevron.open { transform: rotate(180deg); }

/* Dropdown */
.drp-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  z-index: 200;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.15);
  padding: 14px;
  width: 520px;
  user-select: none;
}

/* Transition */
.drp-pop-enter-active { transition: opacity 0.15s, transform 0.15s; }
.drp-pop-leave-active { transition: opacity 0.1s, transform 0.1s; }
.drp-pop-enter-from { opacity: 0; transform: translateY(-6px); }
.drp-pop-leave-to { opacity: 0; transform: translateY(-4px); }

/* Quick buttons */
.drp-quick {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
}
.drp-quick-btn {
  padding: 5px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  background: #f8fafc;
  font-size: 12px;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}
.drp-quick-btn:hover { background: #f1f5f9; border-color: #cbd5e1; }
.drp-quick-btn.selected {
  background: #ffaa00;
  border-color: #ffaa00;
  color: #1a1a1a;
}

/* Calendar grid */
.drp-calendars {
  display: flex;
  gap: 16px;
}
.drp-month { flex: 1; }
.drp-month-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.drp-month-title {
  font-size: 13px;
  font-weight: 700;
  color: #1a1a1a;
  text-transform: capitalize;
}
.drp-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  transition: background 0.12s;
}
.drp-nav:hover { background: #f1f5f9; }
.drp-nav:disabled { opacity: 0.25; cursor: default; }
.drp-nav:disabled:hover { background: transparent; }

.drp-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  margin-bottom: 4px;
}
.drp-weekdays span {
  text-align: center;
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  padding: 4px 0;
}

.drp-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
}
.drp-day {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  aspect-ratio: 1;
  border: none;
  border-radius: 8px;
  background: transparent;
  font-size: 12px;
  font-weight: 600;
  color: #1a1a1a;
  cursor: pointer;
  transition: background 0.1s, color 0.1s;
  font-family: inherit;
  position: relative;
}
.drp-day:disabled {
  cursor: default;
  color: transparent;
}
.drp-day:not(:disabled):hover {
  background: #f1f5f9;
}
.drp-day.is-start,
.drp-day.is-end {
  background: #ffaa00 !important;
  color: #1a1a1a !important;
  font-weight: 700;
}
.drp-day.in-range {
  background: #fff7e6;
  border-radius: 0;
}
.drp-day.is-start { border-radius: 8px 0 0 8px; }
.drp-day.is-end { border-radius: 0 8px 8px 0; }
.drp-day.is-start.is-end { border-radius: 8px; }

/* Actions */
.drp-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
}
.drp-btn-clear {
  padding: 6px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: #fff;
  font-size: 12px;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  font-family: inherit;
}
.drp-btn-clear:hover { background: #f1f5f9; }
.drp-btn-apply {
  padding: 6px 16px;
  border: none;
  border-radius: 8px;
  background: #ffaa00;
  font-size: 12px;
  font-weight: 700;
  color: #1a1a1a;
  cursor: pointer;
  font-family: inherit;
}
.drp-btn-apply:hover { background: #e69900; }

/* Dark mode */
html.dark .drp-trigger { background: #1e293b; border-color: #475569; color: #f1f5f9; }
html.dark .drp-trigger:hover { border-color: #64748b; }
html.dark .drp-trigger.active { border-color: #ffaa00; }
html.dark .drp-label { color: #94a3b8; }
html.dark .drp-dropdown { background: #1e293b; border-color: #334155; }
html.dark .drp-month-title { color: #f1f5f9; }
html.dark .drp-day { color: #e2e8f0; }
html.dark .drp-day:not(:disabled):hover { background: #334155; }
html.dark .drp-day.in-range { background: #334155; }
html.dark .drp-quick-btn { background: #1e293b; border-color: #334155; color: #94a3b8; }
html.dark .drp-quick-btn:hover { background: #334155; }
html.dark .drp-btn-clear { background: #1e293b; border-color: #475569; color: #94a3b8; }
html.dark .drp-nav { color: #94a3b8; }
html.dark .drp-nav:hover { background: #334155; }

@media (max-width: 768px) {
  .drp { width: 100%; }
  .drp-trigger {
    width: 100%;
    justify-content: center;
    padding: 12px 14px;
    font-size: 14px;
    border-radius: 10px;
  }
  .drp-dropdown {
    position: fixed;
    top: auto;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: calc(100% - 24px);
    max-width: 380px;
    border-radius: 16px 16px 0 0;
    padding: 12px 10px;
    max-height: 70vh;
    overflow-y: auto;
    z-index: 999;
  }
  .drp-quick {
    gap: 4px;
    margin-bottom: 8px;
    padding-bottom: 8px;
    justify-content: center;
    flex-wrap: wrap;
  }
  .drp-quick-btn {
    padding: 5px 10px;
    font-size: 11px;
    border-radius: 16px;
  }
  .drp-calendars {
    flex-direction: column;
    gap: 8px;
  }
  .drp-month-header {
    margin-bottom: 2px;
  }
  .drp-month-title {
    font-size: 12px;
  }
  .drp-nav {
    width: 22px;
    height: 22px;
  }
  .drp-weekdays span {
    font-size: 9px;
    padding: 2px 0;
  }
  .drp-days {
    gap: 0;
  }
  .drp-day {
    font-size: 11px;
    height: 30px;
    border-radius: 6px;
  }
  .drp-actions {
    margin-top: 8px;
    padding-top: 8px;
  }
  .drp-btn-clear,
  .drp-btn-apply {
    padding: 9px 16px;
    font-size: 13px;
    border-radius: 8px;
    flex: 1;
  }
}
</style>
