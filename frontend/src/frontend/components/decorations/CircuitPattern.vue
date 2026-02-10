<template>
  <div class="absolute inset-0 pointer-events-none overflow-hidden opacity-[0.03] dark:opacity-[0.05]">
    <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <pattern id="circuit" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse">
          <path d="M10 10 h80 v80 h-80 z" fill="none" stroke="currentColor" stroke-width="1"/>
          <path d="M20 20 l20 20 h20" fill="none" stroke="currentColor" stroke-width="1"/>
          <path d="M80 80 l-20 -20 h-20" fill="none" stroke="currentColor" stroke-width="1"/>
          <circle cx="20" cy="20" r="2" fill="currentColor"/>
          <circle cx="80" cy="80" r="2" fill="currentColor"/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#circuit)" />
    </svg>
  </div>
</template>
