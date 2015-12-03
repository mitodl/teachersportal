import React from 'react';
import Textfield from 'react-mdl';
import Modal from 'elemental/lib/components/Modal';
import ModalHeader from 'elemental/lib/components/ModalHeader';
import ModalBody from 'elemental/lib/components/ModalBody';
import ModalFooter from 'elemental/lib/components/ModalFooter';
import Button from 'elemental/lib/components/Button';

class LoginModal extends React.Component {
  render() {
    // const { onHideLoginModal, isOpen } = this.props;

    return <Modal>
      <ModalHeader text="Modal Header" />
      <ModalBody>[...Body...]
      </ModalBody>
      <ModalFooter>
      <Button type="primary" onClick={this.toggleModal}>Close modal</Button>
      </ModalFooter>
    </Modal>
    ;
  }
}

// LoginModal.propTypes = {
//   isOpen: React.PropTypes.bool.isRequired,
//   onHideLoginModal: React.PropTypes.func.isRequired
// }

export default LoginModal;
