# Summary (qwen3)

- **Key Takeaway for Startups**  
  - If you're a startup working on new computing technology, you shouldn't aim for a 10x improvement.  
  - You should aim for a 10,000x improvement, but nobody will fund that.  

- **AI and Energy Consumption**  
  - Big tech CEOs are making specific claims about the near future of AI.  
  - They predict that AI will be used all the time within a few years.  
  - These claims lead to increased stock prices and public excitement.  
  - However, they also raise questions about the actual cost of such a future.  

- **Energy Requirements for AI**  
  - AI uses electricity, and the more it is used, the more electricity is consumed.  
  - Transformers have a simple formula to predict resource utilization.  
  - A Drake equation-type model can estimate the power required for global AI usage.  
  - If all humans had an agentic AI assistant, it would draw about half of the total US grid.  
  - Extending this to video models (like Mark Zuckerberg’s glasses) would require 10x to 30x the total grid.  
  - Robotic applications would require hundreds of thousands of times more power.  

- **Extrapolation and Realism**  
  - These numbers are wild extrapolations and likely off by a factor of 10 or 100.  
  - The numbers are meant to give an order of magnitude of what's possible.  
  - There's a huge gap between expectations and reality.  
  - Video models would require about 20,000 gigawatts compared to the current 500 gigawatts.  

- **Options for Realizing the AI Future**  
  - Option 1: Produce more energy.  
    - Tech companies are becoming energy suppliers with gigawatt-scale projects.  
    - Energy tech is a hard path for startups.  
    - One gigawatt project is massive and not enough for the required scale.  
    - It would take a global effort, potentially leading to something like a Dyson sphere.  
  - Option 2: Make computers more efficient.  
    - This is a hard technical problem requiring expertise in both hardware and algorithms.  
    - GPUs are improving exponentially, making it hard for startups to compete.  

- **Challenges in Making Computers More Efficient**  
  - Energy is mostly spent on charging capacitors in current computers.  
  - Voltage changes in metal cause energy consumption.  
  - Capacitance is already as small as possible.  
  - Voltage is constrained by thermodynamic considerations (thermal voltage).  
  - Lower voltage leads to exponential increases in energy consumption due to off-current.  
  - This creates a rock in a hard place: both constraints limit efficiency.  

- **Solutions to Improve Efficiency**  
  - Photonic computing (using light instead of electricity).  
  - Adiabatic logic (eliminating charging schemes).  
  - Quantum computing (low voltages, but very hard).  
  - Probabilistic computing: using intrinsic thermal noise as a computational resource.  
  - This approach is natural for machine learning, which often uses probabilistic models.  

- **Extropic’s Approach**  
  - Extropic is working on a minimal version of probabilistic computing.  
  - They’ve created a probabilistic hardware system that performs generative modeling.  
  - They’ve compared their system with traditional GPU-based algorithms like VAEs and GANS on the Fashion-MNIST dataset.  
  - Their system uses about four times less energy than VAEs for performance parity.  
  - This is a significant improvement and a step toward solving the energy problem.  

- **Probabilistic Hardware and Energy-Based Models**  
  - Energy-based models (EBMs) are not good on their own due to intractable sampling.  
  - Denoising diffusion models can be combined with EBMs to handle complex sampling.  
  - Their probabilistic hardware can approximate large steps in the reverse process of denoising models.  
  - This alleviates the intractable sampling problem in EBMs.  
  - They’ve developed a probabilistic hardware architecture that can be used efficiently in machine learning.  

- **Key Technology Developed**  
  - A mass-manufacturable source of randomness.  
  - They’ve cracked the problem of harnessing transistor noise for computational tasks.  
  - They’ve built a test chip and validated their theory.  
  - The circuit uses a few transistors and generates random bits with low energy consumption.  
  - It is 10,000 times more efficient than traditional random number generators.  

- **Future Goals and Research**  
  - They aim to build a real computer using probabilistic hardware instead of just a simulation.  
  - They’re working on combining probabilistic computing with traditional neural networks.  
  - They’re using autoencoders and GANs to embed complex data into probabilistic computers.  
  - They’re exploring generative modeling in latent space using structured noise.  
  - They’re aiming for an order of magnitude improvement, with potential for even more.  

- **Collaboration and Opportunities**  
  - They’re looking to bring on a cohort of research residents.  
  - They’re excited about hybrid machine learning approaches.  
  - They have an elite analog design team with over 75 years of experience.  
  - They have specialized talent in transistor noise modeling and probabilistic machine learning.  
  - They’re launching an early access program for their hardware and algorithms.  
  - A QR code is provided for interested individuals to learn more and sign up.