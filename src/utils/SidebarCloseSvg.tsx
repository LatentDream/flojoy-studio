type ThemeProp = {
  theme: "light" | "dark";
};

const CloseIconSvg = ({ theme }: ThemeProp) => {
  return (
    <div>
      {theme === "dark" ? (
        <svg
          width="9"
          height="9"
          viewBox="0 0 9 9"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M8.73258 0.982585C8.78603 0.929203 8.82844 0.865816 8.85739 0.796043C8.88634 0.726271 8.90127 0.651479 8.90132 0.575938C8.90136 0.500398 8.88653 0.425588 8.85766 0.35578C8.8288 0.285972 8.78647 0.222533 8.73309 0.169085C8.6797 0.115637 8.61632 0.0732267 8.54654 0.0442758C8.47677 0.0153248 8.40198 0.000400004 8.32644 0.000353575C8.2509 0.000307145 8.17609 0.01514 8.10628 0.0440052C8.03647 0.0728703 7.97303 0.115202 7.91958 0.168585L4.45058 3.63758L0.982585 0.168585C0.874642 0.0606417 0.728239 -1.13737e-09 0.575585 0C0.42293 1.13737e-09 0.276528 0.0606417 0.168585 0.168585C0.0606417 0.276528 1.13737e-09 0.42293 0 0.575585C-1.13737e-09 0.728239 0.0606417 0.874642 0.168585 0.982585L3.63758 4.45058L0.168585 7.91859C0.115137 7.97203 0.0727396 8.03549 0.0438137 8.10532C0.0148879 8.17515 0 8.25 0 8.32558C0 8.40117 0.0148879 8.47602 0.0438137 8.54585C0.0727396 8.61568 0.115137 8.67914 0.168585 8.73258C0.276528 8.84053 0.42293 8.90117 0.575585 8.90117C0.651172 8.90117 0.726019 8.88628 0.795852 8.85736C0.865685 8.82843 0.929137 8.78603 0.982585 8.73258L4.45058 5.26358L7.91958 8.73258C8.02753 8.84039 8.17388 8.90091 8.32644 8.90082C8.479 8.90072 8.62527 8.84003 8.73309 8.73208C8.8409 8.62414 8.90141 8.47779 8.90132 8.32523C8.90122 8.17267 8.84053 8.0264 8.73258 7.91859L5.26358 4.45058L8.73258 0.982585Z"
            fill="#94F4FC"
          />
        </svg>
      ) : (
        <svg
          width="9"
          height="9"
          viewBox="0 0 9 9"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M8.73258 0.982585C8.78603 0.929203 8.82844 0.865816 8.85739 0.796043C8.88634 0.726271 8.90127 0.651479 8.90132 0.575938C8.90136 0.500398 8.88653 0.425588 8.85766 0.35578C8.8288 0.285972 8.78647 0.222533 8.73309 0.169085C8.6797 0.115637 8.61632 0.0732267 8.54654 0.0442758C8.47677 0.0153248 8.40198 0.000400004 8.32644 0.000353575C8.2509 0.000307145 8.17609 0.01514 8.10628 0.0440052C8.03647 0.0728703 7.97303 0.115202 7.91958 0.168585L4.45058 3.63758L0.982585 0.168585C0.874642 0.0606417 0.728239 -1.13737e-09 0.575585 0C0.42293 1.13737e-09 0.276528 0.0606417 0.168585 0.168585C0.0606417 0.276528 1.13737e-09 0.42293 0 0.575585C-1.13737e-09 0.728239 0.0606417 0.874642 0.168585 0.982585L3.63758 4.45058L0.168585 7.91859C0.115137 7.97203 0.0727396 8.03548 0.0438137 8.10532C0.0148879 8.17515 0 8.25 0 8.32558C0 8.40117 0.0148879 8.47602 0.0438137 8.54585C0.0727396 8.61568 0.115137 8.67914 0.168585 8.73258C0.276528 8.84053 0.42293 8.90117 0.575585 8.90117C0.651172 8.90117 0.726019 8.88628 0.795852 8.85736C0.865685 8.82843 0.929137 8.78603 0.982585 8.73258L4.45058 5.26358L7.91958 8.73258C8.02753 8.84039 8.17388 8.90091 8.32644 8.90082C8.479 8.90072 8.62528 8.84003 8.73309 8.73208C8.8409 8.62414 8.90141 8.47779 8.90132 8.32523C8.90122 8.17267 8.84053 8.0264 8.73258 7.91859L5.26358 4.45058L8.73258 0.982585Z"
            fill="black"
          />
        </svg>
      )}
    </div>
  );
};

export default CloseIconSvg;
