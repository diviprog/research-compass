/**
 * NeoCampus Design Tokens
 * Production-level design system primitives and semantic tokens
 */

// ============================================================================
// PRIMITIVE TOKENS - Raw values that form the foundation
// ============================================================================

export const primitives = {
  colors: {
    // Campus Blue family
    blue: {
      50: '#E6F2FF',
      100: '#CCE4FF',
      200: '#99CAFF',
      300: '#66AFFF',
      400: '#3395FF',
      500: '#0070F3', // Primary
      600: '#0060D9',
      700: '#0050BF',
      800: '#0040A6',
      900: '#00308C',
    },
    
    // Slate family
    slate: {
      50: '#F8FAFC',
      100: '#F1F5F9',
      200: '#E5E7EB', // Secondary
      300: '#CBD5E1',
      400: '#94A3B8',
      500: '#64748B',
      600: '#475569',
      700: '#334155',
      800: '#1E293B',
      900: '#0F172A',
    },
    
    // Coral Signal family
    coral: {
      50: '#FEF2F2',
      100: '#FEE2E2',
      200: '#FECACA',
      300: '#FCA5A5',
      400: '#F87171', // Accent
      500: '#EF4444',
      600: '#DC2626',
      700: '#B91C1C',
      800: '#991B1B',
      900: '#7F1D1D',
    },
    
    // Mint Green family
    mint: {
      50: '#ECFDF5',
      100: '#D1FAE5',
      200: '#A7F3D0',
      300: '#6EE7B7',
      400: '#34D399',
      500: '#10B981', // Success
      600: '#059669',
      700: '#047857',
      800: '#065F46',
      900: '#064E3B',
    },
    
    // Neutrals
    white: '#FFFFFF',
    black: '#000000',
    offWhite: '#FAFAFA',
  },
  
  spacing: {
    0: '0px',
    1: '4px',   // 4pt baseline
    2: '8px',
    3: '12px',
    4: '16px',
    5: '20px',
    6: '24px',
    7: '28px',
    8: '32px',
    10: '40px',
    12: '48px',
    16: '64px',
    20: '80px',
    24: '96px',
    32: '128px',
  },
  
  typography: {
    fontFamily: {
      display: 'Satoshi, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      body: '"Roboto Flex", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      mono: '"Roboto Mono", "Fira Code", monospace',
    },
    
    fontSize: {
      xs: '12px',
      sm: '14px',
      base: '16px',
      lg: '18px',
      xl: '20px',
      '2xl': '24px',
      '3xl': '28px',
      '4xl': '36px',
      '5xl': '44px',
    },
    
    fontWeight: {
      regular: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    
    lineHeight: {
      tight: 1.2,
      snug: 1.375,
      normal: 1.5,
      relaxed: 1.625,
      loose: 2,
    },
    
    letterSpacing: {
      tighter: '-0.02em',
      tight: '-0.01em',
      normal: '0em',
      wide: '0.01em',
      wider: '0.02em',
      widest: '0.05em',
    },
  },
  
  borderRadius: {
    none: '0px',
    sm: '4px',
    base: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
    full: '9999px',
  },
  
  shadows: {
    none: 'none',
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    
    // Elevation system for z-depth
    elevation1: '0 1px 3px rgba(0, 112, 243, 0.08)',
    elevation2: '0 4px 8px rgba(0, 112, 243, 0.12)',
    elevation3: '0 8px 16px rgba(0, 112, 243, 0.16)',
    elevation4: '0 16px 32px rgba(0, 112, 243, 0.2)',
  },
  
  motion: {
    duration: {
      instant: '50ms',
      fast: '150ms',
      normal: '250ms',
      slow: '350ms',
      slower: '500ms',
    },
    
    easing: {
      linear: 'linear',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
      
      // Custom signature easings
      campusSnap: 'cubic-bezier(0.34, 1.56, 0.64, 1)', // Snappy entrance
      campusSlide: 'cubic-bezier(0.16, 1, 0.3, 1)',    // Smooth slide
      campusFloat: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)', // Gentle float
    },
  },
  
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
  
  zIndex: {
    base: 0,
    dropdown: 1000,
    sticky: 1100,
    fixed: 1200,
    modalBackdrop: 1300,
    modal: 1400,
    popover: 1500,
    tooltip: 1600,
  },
} as const;

// ============================================================================
// SEMANTIC TOKENS - Context-aware values mapped from primitives
// ============================================================================

export const semantic = {
  colors: {
    // Brand
    primary: {
      default: primitives.colors.blue[500],
      hover: primitives.colors.blue[600],
      active: primitives.colors.blue[700],
      disabled: primitives.colors.blue[200],
      subtle: primitives.colors.blue[50],
    },
    
    secondary: {
      default: primitives.colors.slate[200],
      hover: primitives.colors.slate[300],
      active: primitives.colors.slate[400],
    },
    
    accent: {
      default: primitives.colors.coral[400],
      hover: primitives.colors.coral[500],
      active: primitives.colors.coral[600],
      subtle: primitives.colors.coral[50],
    },
    
    success: {
      default: primitives.colors.mint[500],
      hover: primitives.colors.mint[600],
      active: primitives.colors.mint[700],
      subtle: primitives.colors.mint[50],
    },
    
    // Surface colors
    surface: {
      background: primitives.colors.offWhite,
      paper: primitives.colors.white,
      elevated: primitives.colors.white,
      overlay: 'rgba(0, 0, 0, 0.4)',
    },
    
    // Text colors
    text: {
      primary: primitives.colors.slate[900],
      secondary: primitives.colors.slate[600],
      tertiary: primitives.colors.slate[500],
      disabled: primitives.colors.slate[400],
      inverse: primitives.colors.white,
      link: primitives.colors.blue[500],
      linkHover: primitives.colors.blue[700],
    },
    
    // Border colors
    border: {
      default: primitives.colors.slate[200],
      hover: primitives.colors.slate[300],
      focus: primitives.colors.blue[500],
      error: primitives.colors.coral[400],
    },
    
    // Status colors
    status: {
      info: primitives.colors.blue[500],
      success: primitives.colors.mint[500],
      warning: '#F59E0B',
      error: primitives.colors.coral[500],
    },
  },
  
  typography: {
    // Display hierarchy
    display: {
      xl: {
        fontSize: primitives.typography.fontSize['5xl'],
        fontWeight: primitives.typography.fontWeight.bold,
        lineHeight: primitives.typography.lineHeight.tight,
        letterSpacing: primitives.typography.letterSpacing.tighter,
        fontFamily: primitives.typography.fontFamily.display,
      },
      lg: {
        fontSize: primitives.typography.fontSize['4xl'],
        fontWeight: primitives.typography.fontWeight.bold,
        lineHeight: primitives.typography.lineHeight.tight,
        letterSpacing: primitives.typography.letterSpacing.tight,
        fontFamily: primitives.typography.fontFamily.display,
      },
    },
    
    // Heading hierarchy
    heading: {
      h1: {
        fontSize: primitives.typography.fontSize['3xl'],
        fontWeight: primitives.typography.fontWeight.semibold,
        lineHeight: primitives.typography.lineHeight.snug,
        fontFamily: primitives.typography.fontFamily.display,
      },
      h2: {
        fontSize: primitives.typography.fontSize['2xl'],
        fontWeight: primitives.typography.fontWeight.semibold,
        lineHeight: primitives.typography.lineHeight.snug,
        fontFamily: primitives.typography.fontFamily.display,
      },
      h3: {
        fontSize: primitives.typography.fontSize.xl,
        fontWeight: primitives.typography.fontWeight.semibold,
        lineHeight: primitives.typography.lineHeight.normal,
        fontFamily: primitives.typography.fontFamily.display,
      },
    },
    
    // Body text
    body: {
      lg: {
        fontSize: primitives.typography.fontSize.lg,
        fontWeight: primitives.typography.fontWeight.regular,
        lineHeight: primitives.typography.lineHeight.relaxed,
        fontFamily: primitives.typography.fontFamily.body,
      },
      base: {
        fontSize: primitives.typography.fontSize.base,
        fontWeight: primitives.typography.fontWeight.regular,
        lineHeight: primitives.typography.lineHeight.normal,
        fontFamily: primitives.typography.fontFamily.body,
      },
      sm: {
        fontSize: primitives.typography.fontSize.sm,
        fontWeight: primitives.typography.fontWeight.regular,
        lineHeight: primitives.typography.lineHeight.normal,
        fontFamily: primitives.typography.fontFamily.body,
      },
    },
    
    // Labels
    label: {
      fontSize: primitives.typography.fontSize.xs,
      fontWeight: primitives.typography.fontWeight.semibold,
      lineHeight: primitives.typography.lineHeight.tight,
      letterSpacing: primitives.typography.letterSpacing.widest,
      textTransform: 'uppercase' as const,
      fontFamily: primitives.typography.fontFamily.body,
    },
  },
  
  spacing: {
    section: primitives.spacing[20],
    component: primitives.spacing[6],
    element: primitives.spacing[4],
    inline: primitives.spacing[2],
  },
  
  motion: {
    // Entrance animations
    entrance: {
      duration: primitives.motion.duration.fast,
      easing: primitives.motion.easing.campusSnap,
    },
    
    // Exit animations
    exit: {
      duration: primitives.motion.duration.fast,
      easing: primitives.motion.easing.easeIn,
    },
    
    // Interactive feedback
    interaction: {
      duration: primitives.motion.duration.instant,
      easing: primitives.motion.easing.easeOut,
    },
    
    // Content transitions
    content: {
      duration: primitives.motion.duration.normal,
      easing: primitives.motion.easing.campusSlide,
    },
    
    // Floating elements
    float: {
      duration: primitives.motion.duration.slow,
      easing: primitives.motion.easing.campusFloat,
    },
  },
} as const;

// ============================================================================
// COMPONENT TOKENS - Specific token sets for components
// ============================================================================

export const components = {
  card: {
    padding: primitives.spacing[6],
    borderRadius: primitives.borderRadius.lg,
    background: semantic.colors.surface.paper,
    border: `1px solid ${semantic.colors.border.default}`,
    shadow: primitives.shadows.elevation1,
    hoverShadow: primitives.shadows.elevation3,
    transition: `all ${semantic.motion.interaction.duration} ${semantic.motion.interaction.easing}`,
  },
  
  button: {
    borderRadius: primitives.borderRadius.base,
    fontWeight: primitives.typography.fontWeight.semibold,
    transition: `all ${semantic.motion.interaction.duration} ${semantic.motion.interaction.easing}`,
    
    sizes: {
      sm: { height: '32px', padding: `0 ${primitives.spacing[3]}`, fontSize: primitives.typography.fontSize.sm },
      md: { height: '40px', padding: `0 ${primitives.spacing[4]}`, fontSize: primitives.typography.fontSize.base },
      lg: { height: '48px', padding: `0 ${primitives.spacing[6]}`, fontSize: primitives.typography.fontSize.lg },
    },
  },
  
  input: {
    borderRadius: primitives.borderRadius.base,
    border: `1px solid ${semantic.colors.border.default}`,
    focusBorder: `1px solid ${semantic.colors.border.focus}`,
    padding: `${primitives.spacing[2]} ${primitives.spacing[3]}`,
    fontSize: primitives.typography.fontSize.base,
    transition: `all ${semantic.motion.interaction.duration} ${semantic.motion.interaction.easing}`,
  },
  
  badge: {
    borderRadius: primitives.borderRadius.full,
    padding: `${primitives.spacing[1]} ${primitives.spacing[2]}`,
    fontSize: primitives.typography.fontSize.xs,
    fontWeight: primitives.typography.fontWeight.semibold,
  },
  
  modal: {
    borderRadius: primitives.borderRadius.xl,
    padding: primitives.spacing[6],
    maxWidth: '768px',
    background: semantic.colors.surface.paper,
    shadow: primitives.shadows['2xl'],
  },
} as const;

// Type exports for TypeScript
export type Primitives = typeof primitives;
export type Semantic = typeof semantic;
export type Components = typeof components;

