/* eslint-disable react/no-unescaped-entities */
/* eslint-disable max-len */
// eslint-disable-next-line no-unused-vars
function About() {
  return (

    <>
      <ModalBtn modalID="about-modal" addlClasses="btn-ghost w-16"><i className="fa-solid fa-rainbow" title="About" /></ModalBtn>

      <ModalBox modalID="about-modal">
        <ModalTitle>ABOUT</ModalTitle>

        <Heading3>What is BitBuddy?</Heading3>
        <p className="pb-4">BitBuddy is a virtual pet app inspired by digital pet games from the early/mid 2000s, but with a modern twist: AI. It was created by Arsen as part of his capstone project for the course SOFTWARE ENGINEERING PROJECT 1 </p>
        

        <Heading3>Who is Arsen?</Heading3>
        <p className="pb-4">Arsen is a software engineer based in Kenya. BitBuddy is a nod to Arsen's first exposure to tech: as an avid Neopets player growing up, he loves to tinker with things.</p>
        <p>
          You can find Arsen on
          {' '}
          <a
            href="https://github.com/arsenhh-byte/"
            className="link hover:bg-accent"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
          {' '}
          and
          {' '}
          <a
            href="https://www.linkedin.com/in/arsen-h-b7aba919b/"
            className="link hover:bg-accent"
            target="_blank"
            rel="noopener noreferrer"
          >
            LinkedIn
          </a>
          .
        </p>
        <ModalFooter>
          <ModalBtn modalID="about-modal">
            Close
          </ModalBtn>
        </ModalFooter>
      </ModalBox>
    </>
  );
}
