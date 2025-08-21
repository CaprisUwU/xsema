import React from "react";
import './Badges.css'; // Optional: for custom styling

const BADGE_CONFIG = {
  symbolic: {
    icon: "🔍",
    label: "Rare Pattern",
    color: "indigo",
    tooltip: "This NFT has unique patterns that make it stand out in its collection"
  },
  structural: {
    icon: "🧩",
    label: "Unique Traits",
    color: "teal",
    tooltip: "Features rare characteristics that make it one-of-a-kind"
  },
  golden: {
    icon: "✨",
    label: "Perfect Balance",
    color: "goldenrod",
    tooltip: "Exhibits exceptional harmony in its design and traits"
  },
  hybrid: {
    icon: "🏆",
    label: "Premium Score",
    color: "deepskyblue",
    tooltip: "Top-rated based on multiple rarity factors"
  },
  clone: {
    icon: "⚠️",
    label: "Exercise Caution",
    color: "orangered",
    tooltip: "Additional verification recommended - check authenticity carefully"
  },
  unique: {
    icon: "✅",
    label: "Verified Original",
    color: "mediumseagreen",
    tooltip: "Authentic and unique in the collection"
  }
};

// Map of new flag names to badge types
const BADGE_TYPE_MAP = {
  showRarePattern: 'symbolic',
  showUniqueTraits: 'structural',
  showPerfectBalance: 'golden',
  showPremiumScore: 'hybrid',
  showCaution: 'clone',
  showVerified: 'unique'
};

export function Badges({ flags }) {
  // Get active badge types based on flags
  const activeBadges = Object.entries(flags)
    .filter(([flag, isActive]) => isActive && BADGE_TYPE_MAP[flag])
    .map(([flag]) => BADGE_TYPE_MAP[flag]);

  return (
    <div className="badges-container">
      {activeBadges.map((badgeType) => {
        const config = BADGE_CONFIG[badgeType];
        return config ? (
          <span
            key={badgeType}
            className={`badge ${badgeType}-badge`}
            title={config.tooltip}
            style={{ backgroundColor: config.color }}
          >
            {config.icon} {config.label}
          </span>
        ) : null;
      })}
    </div>
  );
}
