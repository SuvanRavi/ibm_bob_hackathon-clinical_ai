interface BrandMarkProps {
  size?: number
}

export function BrandMark({ size = 18 }: BrandMarkProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M12 4 L12 9 M12 15 L12 20 M4 12 L9 12 M15 12 L20 12"
        stroke="#141413"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  )
}
