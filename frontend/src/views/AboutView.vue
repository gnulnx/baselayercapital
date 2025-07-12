<template>
  <div class="about hcentered-content">
    <div class="about-container">
      <h1>About Base Layer Capital</h1>
      <p>
        Base Layer Capital (BLC) is a modern family office and capital management platform built on Bitcoin.
      </p>
      <p>
        Bitcoin is, in our view, the most important financial innovation of our time and will fundamentally reshape the global financial system.
      </p>
      <p>
        The current financial system is built on fiat currencies subject to inflation, manipulation, and systemic risk, creating a misalignment between the incentives of traditional financial institutions and the long-term interests of individuals and society.
      </p>
      <p>
  Bitcoin is fundamentally different: it is governed by transparent, predictable monetary policy and secured by a decentralized network that resists censorship, manipulation, and control by any single party. Its fixed supply and open protocol design align perfectly with long-term incentives, offering a foundation of trustless security and absolute scarcity unmatched by any legacy asset.
</p>
<p>
        As such, we view Bitcoin as the only reasonable monetary foundation on which to build a modern company.
      </p>

      
      <p>
        BLC operates as a modern capital platform, utilizing Bitcoin as pristine collateral to fund strategic growth opportunities while preserving our Bitcoin-denominated balance sheet. 
        This approach allows us to pursue asymmetric outcomes while maintaining discipline and resilience through changing market cycles.
      </p>
      <p>
        Through transparency and careful stewardship, we will share insights into how we operate BLC as a Bitcoin-aligned holding company.
      </p>
      <p>
        Thank you for following along as we build a platform for the Bitcoin era.
      </p>
    </div>
  </div>
</template>


<style scoped lang="scss">
@use '@/assets/scss/variables.scss' as *;

.about.hcentered-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: calc($nav-total-offset + 0.25rem);
  color: #f0f0f0;
  padding: 0.25rem;
}

.about-container {
  padding: 2rem;
  border: 1px solid orange;
  border-radius: 8px;
  max-width: 800px;
}

h1 {
  text-align: center;
  font-weight: bold;
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

p {
  margin-bottom: 1rem;
  text-align: center;
  line-height: 1.5;
  color: #ccc;
}
</style>
